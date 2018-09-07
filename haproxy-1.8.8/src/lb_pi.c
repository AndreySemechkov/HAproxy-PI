/*
 * Persistent Idle load balancing algorithm.
 *
 * Copyright 2000-2009 Willy Tarreau <w@1wt.eu>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version
 * 2 of the License, or (at your option) any later version.
 *
 */

#include <common/compat.h>
#include <common/config.h>
#include <common/debug.h>
#include <eb32tree.h>

#include <types/global.h>
#include <types/server.h>

#include <proto/backend.h>
#include <proto/queue.h>


/* Remove a server from a tree. It must have previously been dequeued. This
 * function is meant to be called when a server is going down or has its
 * weight disabled.
 */
static inline void pi_remove_from_tree(struct server *s)
{
    s->lb_tree = NULL;
}

/* simply removes a server from a tree */
static inline void pi_dequeue_srv(struct server *s)
{
    eb32_delete(&s->lb_node);
}

/* Queue a server in its associated tree.
 * Servers are sorted by the number of connections.
 * It is important to understand that the server weight is not used
 * here.
 */
static inline void pi_queue_srv(struct server *s)
{
    s->lb_node.key = s->served + s->nbpend;
    eb32_insert(s->lb_tree, &s->lb_node);
}

/* Re-position the server in the pi tree after it has been assigned one
 * connection or after it has released one. Note that it is possible that
 * the server has been moved out of the tree due to failed health-checks.
 */
static void pi_srv_reposition(struct server *s)
{
    if (!s->lb_tree)
        return;

    HA_SPIN_LOCK(LBPRM_LOCK, &s->proxy->lbprm.lock);
    pi_dequeue_srv(s);
    pi_queue_srv(s);
    HA_SPIN_UNLOCK(LBPRM_LOCK, &s->proxy->lbprm.lock);
}

/* This function updates the server trees according to server <srv>'s new
 * state. It should be called when server <srv>'s status changes to down.
 * It is not important whether the server was already down or not. It is not
 * important either that the new state is completely down (the caller may not
 * know all the variables of a server's state).
 */
static void pi_set_server_status_down(struct server *srv)
{
    struct proxy *p = srv->proxy;

    if (!srv_lb_status_changed(srv))
        return;

    if (srv_willbe_usable(srv))
        goto out_update_state;

    if (!srv_currently_usable(srv))
        /* server was already down */
        goto out_update_backend;

    if (srv->flags & SRV_F_BACKUP) {
        p->lbprm.tot_wbck -= srv->cur_eweight;
        p->srv_bck--;

        if (srv == p->lbprm.fbck) {
            /* we lost the first backup server in a single-backup
             * configuration, we must search another one.
             */
            struct server *srv2 = p->lbprm.fbck;
            do {
                srv2 = srv2->next;
            } while (srv2 &&
                     !((srv2->flags & SRV_F_BACKUP) &&
                       srv_willbe_usable(srv2)));
            p->lbprm.fbck = srv2;
        }
    } else {
        p->lbprm.tot_wact -= srv->cur_eweight;
        p->srv_act--;
    }

    pi_dequeue_srv(srv);
    pi_remove_from_tree(srv);

    out_update_backend:
    /* check/update tot_used, tot_weight */
    update_backend_weight(p);
    out_update_state:
    srv_lb_commit_status(srv);
}

/* This function updates the server trees according to server <srv>'s new
 * state. It should be called when server <srv>'s status changes to up.
 * It is not important whether the server was already down or not. It is not
 * important either that the new state is completely UP (the caller may not
 * know all the variables of a server's state). This function will not change
 * the weight of a server which was already up.
 */
static void pi_set_server_status_up(struct server *srv)
{
    struct proxy *p = srv->proxy;

    if (!srv_lb_status_changed(srv))
        return;

    if (!srv_willbe_usable(srv))
        goto out_update_state;

    if (srv_currently_usable(srv))
        /* server was already up */
        goto out_update_backend;

    if (srv->flags & SRV_F_BACKUP) {
        srv->lb_tree = &p->lbprm.pi.bck;
        p->lbprm.tot_wbck += srv->next_eweight;
        p->srv_bck++;

        if (!(p->options & PR_O_USE_ALL_BK)) {
            if (!p->lbprm.fbck) {
                /* there was no backup server anymore */
                p->lbprm.fbck = srv;
            } else {
                /* we may have restored a backup server prior to fbck,
                 * in which case it should replace it.
                 */
                struct server *srv2 = srv;
                do {
                    srv2 = srv2->next;
                } while (srv2 && (srv2 != p->lbprm.fbck));
                if (srv2)
                    p->lbprm.fbck = srv;
            }
        }
    } else {
        srv->lb_tree = &p->lbprm.pi.act;
        p->lbprm.tot_wact += srv->next_eweight;
        p->srv_act++;
    }

    /* note that eweight cannot be 0 here */
    pi_queue_srv(srv);

    out_update_backend:
    /* check/update tot_used, tot_weight */
    update_backend_weight(p);
    out_update_state:
    srv_lb_commit_status(srv);
}

/* This function must be called after an update to server <srv>'s effective
 * weight. It may be called after a state change too.
 */
static void pi_update_server_weight(struct server *srv)
{
    int old_state, new_state;
    struct proxy *p = srv->proxy;

    if (!srv_lb_status_changed(srv))
        return;

    /* If changing the server's weight changes its state, we simply apply
     * the procedures we already have for status change. If the state
     * remains down, the server is not in any tree, so it's as easy as
     * updating its values. If the state remains up with different weights,
     * there are some computations to perform to find a new place and
     * possibly a new tree for this server.
     */

    old_state = srv_currently_usable(srv);
    new_state = srv_willbe_usable(srv);

    if (!old_state && !new_state) {
        srv_lb_commit_status(srv);
        return;
    }
    else if (!old_state && new_state) {
        pi_set_server_status_up(srv);
        return;
    }
    else if (old_state && !new_state) {
        pi_set_server_status_down(srv);
        return;
    }

    if (srv->lb_tree)
        pi_dequeue_srv(srv);

    if (srv->flags & SRV_F_BACKUP) {
        p->lbprm.tot_wbck += srv->next_eweight - srv->cur_eweight;
        srv->lb_tree = &p->lbprm.pi.bck;
    } else {
        p->lbprm.tot_wact += srv->next_eweight - srv->cur_eweight;
        srv->lb_tree = &p->lbprm.pi.act;
    }

    pi_queue_srv(srv);

    update_backend_weight(p);
    srv_lb_commit_status(srv);
}

/* This function is responsible for building the trees in case of Persistent idle
 * It also sets p->lbprm.wdiv to the eweight to uweight ratio. Both active and backup groups are initialized.
 *
 * TODO:
 * This is used for when there are no idle servers and the current server getting the requests goes down.
 * Thus the server that has the least current open http connections will be the next for new connections.
 */
void pi_init_server_tree(struct proxy *p)
{

    /*if(p){
        p->lbprm.pi.log = fopen("~/pi_log", "a");
        if(p->lbprm.pi.log>0)
            fprintf(p->lbprm.pi.log, "Started pi_init_server_tree\n");
    } else{
        printf("pi_init_server_tree p is null");
    }*/

    struct server *srv;
    struct eb_root init_head = EB_ROOT;
    p->lbprm.pi.last_used_node = NULL;
    p->lbprm.set_server_status_up   = pi_set_server_status_up;
    p->lbprm.set_server_status_down = pi_set_server_status_down;
    p->lbprm.update_server_eweight  = pi_update_server_weight;
    p->lbprm.server_take_conn = pi_srv_reposition;
    p->lbprm.server_drop_conn = pi_srv_reposition;

    p->lbprm.wdiv = BE_WEIGHT_SCALE;
    for (srv = p->srv; srv; srv = srv->next) {
        srv->next_eweight = (srv->uweight * p->lbprm.wdiv + p->lbprm.wmult - 1) / p->lbprm.wmult;
        srv_lb_commit_status(srv);
    }

    recount_servers(p);
    update_backend_weight(p);

    p->lbprm.pi.act = init_head;
    p->lbprm.pi.bck = init_head;

    /* queue active and backup servers in two distinct groups */
    for (srv = p->srv; srv; srv = srv->next) {
        if (!srv_currently_usable(srv))
            continue;
        srv->lb_tree = (srv->flags & SRV_F_BACKUP) ? &p->lbprm.pi.bck : &p->lbprm.pi.act;
        pi_queue_srv(srv);
    }
}

/* Return next server from the pi tree in backend <p>. If the tree is empty,
 * return NULL. Saturated servers are skipped.
 */
struct server *pi_get_next_server(struct proxy *p, struct server *srvtoavoid)
{
    struct server *srv, *avoided;
    struct eb32_node *node;
    //p->srv_act = 2;    //TODO

    fprintf(stdout,"\n***inside pi_get_next_server p->srv_act=%d  p->lbprm.fbck=%d*****\n", p->srv_act, p->lbprm.fbck);
    fflush(stdout);
    srv = avoided = NULL;
	
    HA_SPIN_LOCK(LBPRM_LOCK, &p->lbprm.lock);
    if (p->srv_act){
        node = eb32_first(&p->lbprm.pi.act);
        if(node && node->key != 0 && p->lbprm.pi.last_used_node != NULL)
            node = p->lbprm.pi.last_used_node; 
	fprintf(stdout,"\n***inside pi_get_next_server case p->srv_act*****\n");
   	fflush(stdout); 
    } else if (p->lbprm.fbck) {
        srv = p->lbprm.fbck;
        p->lbprm.pi.last_used_node = &(srv->lb_node);
	fprintf(stdout,"\n***inside pi_get_next_server case p->lbprm.fbck*****\n");
   	fflush(stdout); 
        goto out;
    } else if (p->srv_bck){
        node = eb32_first(&p->lbprm.pi.bck);
        if(node && node->key != 0 && p->lbprm.pi.last_used_node != NULL)
            node = p->lbprm.pi.last_used_node;  
	fprintf(stdout,"\n***inside pi_get_next_server case p->srv_bck*****\n");
   	fflush(stdout); 
    } else {
        srv = NULL;
        goto out;
    }
 	 
    fprintf(stdout,"\n****after if's p->lbprm.pi.last_used_node=%li\nnode=%li\nserver=%li****\n", p->lbprm.pi.last_used_node, node,srv);
    fflush(stdout);
    while (node) {
        /*
        OK, we have a server. However, it may be saturated, in which
         * case we don't want to reconsider it for now, so we'll simply
         * skip it. Same if it's the server we try to avoid, in which
         * case we simply remember it for later use if needed.
        */
        struct server *s;
        s = eb32_entry(node, struct server, lb_node);
        if (!s->maxconn || (!s->nbpend && s->served < srv_dynamic_maxconn(s))) {
            if (s != srvtoavoid) {
                srv = s;
                break;
            }
            avoided = s;
        }
        node = eb32_next(node);
    }

//TODO  incase avoided used should last_used_node be (srv==avoided).lb_node or just NULL to avoid bug of going to avoided server with last used.
    // if last_used_node= NULL its like last_used_node died and we take the next best candidate
    if (!srv)
        srv = avoided;
    p->lbprm.pi.last_used_node = &(srv->lb_node);

    out:
    fprintf(stdout,"\n***before exit func next_serv p->lbprm.pi.last_used_node=%li\nnode=%li\nserver=%li*****\n", p->lbprm.pi.last_used_node, node,srv);
    fflush(stdout);
    HA_SPIN_UNLOCK(LBPRM_LOCK, &p->lbprm.lock);
    return srv;
}
