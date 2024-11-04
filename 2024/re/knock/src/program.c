#include <err.h>
#include <net/if.h>
#include <net/pfvar.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/fcntl.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/errno.h>
#include <time.h>
#include <unistd.h>

#define IF "vtnet0"
#define PORT_COMM 1337
#define PORT_FLAG 1337
#define PORT_PHASE1 1
#define PORT_PHASE2 1000

#define NUM_PHASES 3
const char* tablenames[NUM_PHASES] = {"phase1", "phase2", "phase3"};

void print_address(u_int32_t a)
{
	a = ntohl(a);
	printf("%d.%d.%d.%d", a >> 24 & 255, a >> 16 & 255,
		a >> 8 & 255, a & 255);
}

void pass(int dev, u_int32_t ip, int phase)
{
	char needed_create = false;
	struct pfioc_table io_table;
	struct pfioc_table io_table_new;
	struct pfr_addr pfra;
	struct pfr_table tbl;
	struct pfioc_trans trans;
	struct pfioc_trans_e transe[1];
	struct pfioc_pooladdr pp;
	struct pfioc_rule pr;

#ifdef DEBUG
	printf("adding ");
	print_address(ip);
	printf(" to table %d\n", phase);
#endif
	/* add ip to phase table */
	bzero(&pfra, sizeof pfra);
	pfra.pfra_af = AF_INET;
	pfra.pfra_net = 32;
	pfra.pfra_ip4addr.s_addr = ip;
	bzero(&io_table, sizeof io_table);
	strlcpy(io_table.pfrio_table.pfrt_name, tablenames[phase - 1], sizeof(io_table.pfrio_table.pfrt_name));
	io_table.pfrio_buffer = &pfra;
	io_table.pfrio_esize = sizeof(struct pfr_addr);
	io_table.pfrio_size = 1;
	if (ioctl(dev, DIOCRADDADDRS, &io_table) == -1) {
		if (errno == 3) {
			needed_create = true;
			/* create table if it doesn't already exist
			 * The reason this is here instead of setup is to avoid
			 * telegraphing the whole challenge at the beginning.*/

			bzero(&tbl, sizeof(tbl));
			strlcpy(tbl.pfrt_name, tablenames[phase - 1], sizeof(tbl.pfrt_name));
			bzero(&io_table_new, sizeof io_table_new);
			io_table_new.pfrio_buffer = &tbl;
			io_table_new.pfrio_esize = sizeof(tbl);
			io_table_new.pfrio_size = 1;
			if (ioctl(dev, DIOCRADDTABLES, &io_table_new) == -1)
				return;
			if (ioctl(dev, DIOCRADDADDRS, &io_table) == -1)
				return;
		}
	}

	if (!needed_create)
		return;
	/* add relevant rule */
	bzero(&pp, sizeof(pp));
	bzero(&pr, sizeof(pr));
	bzero(&trans, sizeof(trans));
	bzero(&transe, sizeof(transe));

	transe[0].rs_num = PF_RULESET_FILTER;
	trans.size = 1;
	trans.esize = sizeof(transe[0]);
	trans.array = transe;
	if (ioctl(dev, DIOCBEGINADDRS, &pp) == -1)
		return;

	pr.action = PF_CHANGE_GET_TICKET;
	if (ioctl(dev, DIOCCHANGERULE, &pr) == -1)
		return;
	/* pr.ticket = transe[0].ticket; */
	pr.pool_ticket = pp.ticket;
	pr.rule.rtableid = -1;
	pr.action = PF_CHANGE_ADD_TAIL;

	/* pass in on vtnet0 inet proto tcp from <phase1> to any port 1
	 * pass in on vtnet0 inet proto tcp from <phase2> to any port < 1000
	 * pass in on vtnet0 inet proto tcp from <phase3> to any port 1337 keep state (max-src-states 10)
	 */
	pr.rule.action = PF_PASS;
	pr.rule.direction = PF_IN;
	strlcpy(pr.rule.ifname, IF, sizeof(pr.rule.ifname));
	pr.rule.af = AF_INET;
	pr.rule.proto = IPPROTO_TCP;
	pr.rule.dst.port[0] = htons(phase + (PORT_PHASE2-2)*((phase+1)%2) + (PORT_FLAG-3)*(phase/3));
	pr.rule.dst.port_op = phase == 2 ? PF_OP_LT : PF_OP_EQ;
	pr.rule.src.addr.type = PF_ADDR_TABLE;
	strlcpy(pr.rule.src.addr.v.tblname, tablenames[phase - 1], sizeof(tablenames[0]));
	pr.rule.flags = (1<<1);
	pr.rule.flagset = (1<<1) | (1<<4);
	pr.rule.keep_state = PF_STATE_NORMAL;
	/*
	 * BUG: sctp timeout gets set with max_src_states. Fixed in stable:
	 * https://cgit.freebsd.org/src/commit/?h=stable/13&id=d92f239a92c448f2954fd4c14775a36532a78dc6
	 */
	/* pr.rule.max_src_states = phase + 3; */
	/* pr.rule.rule_flag |= PFRULE_SRCTRACK; */
	if(ioctl(dev, DIOCCHANGERULE, &pr) == -1)
		return;
}

char check(int dev, u_int32_t ip, int phase)
{
	struct pfioc_states_v2 ps;

	struct pf_state_export *p;
	char *inbuf = NULL, *newinbuf = NULL;
	unsigned int len, i, j, count, phase3checks, dstport;

	if (phase == 1)
		return true;

	bzero(&ps, sizeof(ps));
	ps.ps_req_version = PF_STATE_VERSION;

	len = 0;
	for (;;) {
		ps.ps_len = len;
		if (len) {
			if ((newinbuf = realloc(inbuf, len)) == NULL)
				return false;
			bzero(newinbuf, len);
			ps.ps_buf = inbuf = newinbuf;
		}
		if (ioctl(dev, DIOCGETSTATESV2, &ps) == -1)
			goto out;
		if (ps.ps_len + sizeof(struct pfioc_states_v2) < len)
			break;
		if (len == 0 && ps.ps_len == 0)
			goto out;
		if (len == 0 && ps.ps_len != 0)
			len = ps.ps_len;
		if (ps.ps_len == 0)
			goto out;   /* no states */
		len *= 2;
	}
	p = ps.ps_states;

	count = 0;
	phase3checks = 0;
	for (i = 0; i < ps.ps_len; i += sizeof(*p), p++) {
		if (ip == p->key[PF_SK_WIRE].addr[0].v4.s_addr) {
			if (++count > 6)
				goto out;
#ifdef DEBUG
			print_address(ip);
			printf(" %d %d\n", htons(p->key[PF_SK_WIRE].port[0]), htons(p->key[PF_SK_WIRE].port[1]));
#endif
			dstport = htons(p->key[PF_SK_WIRE].port[1]);
			if (phase == 2 && dstport == PORT_PHASE1)
				goto good;

			for(j=0; j<32; j+=8)
				if (((ip >> j) & 255) == dstport)
					phase3checks |= 1 << j;
		}
	}
	if (phase3checks != 0x1010101)
		goto out;

good:
	free(inbuf);
	return true;
out:
	free(inbuf);
	return false;
}

/* fork and single thread */
void launch_commserver(void)
{
	int s, i, dev, msg;
	uint32_t recv;
	struct sockaddr_in sa;
	struct sockaddr_in csa;
	struct pfr_addr pfra;
	char phase;
	struct pfioc_table io_table;
	int okmsg = 2124655; /* "ok \x00" */
	socklen_t cb = sizeof csa;

	switch (fork()) {
		case -1:
			exit(3);
		case 0:
			break;
		default:
			return;
	}

	if ((s = socket(PF_INET, SOCK_DGRAM, 0)) < 0) {
		exit(1);
	}

	memset(&sa, '\0', sizeof(sa));

	sa.sin_family = AF_INET;
	sa.sin_port = htons(PORT_COMM);
	sa.sin_addr.s_addr = htonl(INADDR_ANY);

	if (bind(s, (struct sockaddr *)&sa, sizeof sa) < 0) {
		exit(2);
	}

	if ((dev = open("/dev/pf", O_RDWR)) == -1)
		exit(3);
	while (true) {
		recv = 0;
		recvfrom(s, &recv, 4, 0, (struct sockaddr *)&csa, &cb);
		phase = recv >> 24;

		if ((recv & 0xff0000) != 0x200000)
			goto badpacket;
		if (csa.sin_port % 100 != 0)
			goto badpacket;
		if ((recv & 0xffff) != csa.sin_port)
			goto badpacket;

		switch (phase) {
			case '1':
			case '2':
			case '3':
				if (check(dev, csa.sin_addr.s_addr, phase - 0x30))
				{
					pass(dev, csa.sin_addr.s_addr, phase - 0x30);
					msg = okmsg | (phase<<24);
					sendto(s, &msg, 4, 0, (struct sockaddr *)&csa, cb);
					continue;
				}
			default:
				goto badpacket;
		}
badpacket:
		sendto(s, "err!", 4, 0, (struct sockaddr *)&csa, cb);
		/* remove ip from all tables */
		bzero(&io_table, sizeof(io_table));
		bzero(&pfra, sizeof pfra);
		pfra.pfra_af = AF_INET;
		pfra.pfra_net = 32;
		pfra.pfra_ip4addr.s_addr = csa.sin_addr.s_addr;
		io_table.pfrio_buffer = &pfra;
		io_table.pfrio_size = 1;
		io_table.pfrio_esize = sizeof (struct pfr_addr);
		for (i=0; i<NUM_PHASES; ++i) {
			strlcpy(io_table.pfrio_table.pfrt_name, tablenames[i], sizeof(io_table.pfrio_table.pfrt_name));
			ioctl(dev, DIOCRDELADDRS, &io_table);
		}

	}
}

/* fork and sleep if forkloop */
void tableclear(char forkloop)
{
	int dev, i;
	struct pfioc_table io_get;
	struct pfioc_table io_clear;
	struct pfr_table table_buf[NUM_PHASES];

	if (forkloop) {
		switch (fork()) {
			case -1:
				exit(9137);
			case 0:
				break;
			default:
				return;
		}
	}

	if ((dev = open("/dev/pf", O_RDWR)) == -1)
		exit(1);

	bzero(&io_clear, sizeof io_clear);
	while (true) {
		bzero(&io_get, sizeof io_get);
		io_get.pfrio_buffer = table_buf;
		io_get.pfrio_esize = sizeof(struct pfr_table);
		io_get.pfrio_size = NUM_PHASES;
		ioctl(dev, DIOCRGETTABLES, &io_get);

		for (i=0; i<NUM_PHASES; ++i) {
			strlcpy(io_clear.pfrio_table.pfrt_name, tablenames[i], sizeof(io_clear.pfrio_table.pfrt_name));
			ioctl(dev, DIOCRCLRADDRS, &io_clear);
		}

		if (!forkloop)
			return;
		sleep(10 - (time(NULL) % 10));
	}
}

/* fork and single thread */
void launch_voteserver(void)
{
	int s, c;
	struct sockaddr_in sa;
	struct sockaddr_in csa;
	socklen_t b = sizeof sa;
	FILE *client;

	switch (fork()) {
		case -1:
			exit(3);
		case 0:
			break;
		default:
			return;
	}

	if ((s = socket(PF_INET, SOCK_STREAM, 0)) < 0) {
		exit(1);
	}

	memset(&sa, '\0', sizeof(sa));
	memset(&csa, '\0', sizeof(csa));

	sa.sin_family = AF_INET;
	sa.sin_port = htons(PORT_FLAG);
	sa.sin_addr.s_addr = htonl(INADDR_ANY);

	if (bind(s, (struct sockaddr *)&sa, sizeof sa) < 0) {
		exit(2);
	}

	if (listen(s, 20) < 0)
	{
		exit(20);
	}

	b = sizeof sa;
	for (;;) {
		if ((c = accept(s, (struct sockaddr *)&sa, &b)) < 0) {
			continue;
		}

		if ((client = fdopen(c, "w+")) == NULL) {
			continue;
		}

		if(getpeername(c, (struct sockaddr *)&csa, &b) != -1) {
			printf("sending flag to ");
			print_address(csa.sin_addr.s_addr);
			printf("\n");
		}

		fprintf(client, "%s\n", getenv("FLAG"));
		fclose(client);
		tableclear(false);
	}
}

/* parent process */
void setup(void)
{
	struct pfioc_table io_table;
	struct pfioc_trans trans;
	struct pfioc_trans_e transe[10];
	struct pfioc_pooladdr pp;
	struct pfioc_rule pr;
	struct pfioc_tm pt;
	int dev;


	if ((dev = open("/dev/pf", O_RDWR)) == -1)
		exit(1);

	/* start pf */
	ioctl(dev, DIOCSTART);

	/*
	 * --- clear things ---
	 */

	/* clear rules */
	bzero(&trans, sizeof(trans));
	bzero(&transe, sizeof(transe));
	transe[0].rs_num = PF_RULESET_SCRUB;
	transe[1].rs_num = PF_RULESET_FILTER;
	trans.size = 2;
	trans.esize = sizeof(transe[0]);
	trans.array = transe;
	if (ioctl(dev, DIOCXBEGIN, &trans) == -1)
		exit(1);
	if (ioctl(dev, DIOCXCOMMIT, &trans) == -1)
		exit(1);

	/* clear tables */
	bzero(&io_table, sizeof io_table);
	if (ioctl(dev, DIOCRCLRTABLES, &io_table) == -1)
		exit(1);

	/* clear source nodes */
	if (ioctl(dev, DIOCCLRSRCNODES) == -1)
		exit(1);

	/* clear stats */
	if (ioctl(dev, DIOCCLRSTATUS) == -1)
		exit(1);

	/* clear fingerprints */
	if (ioctl(dev, DIOCOSFPFLUSH) == -1)
		exit(1);

	/*
	 * --- add rules ---
	 */

	/* add rules */
	bzero(&pp, sizeof(pp));
	bzero(&pr, sizeof(pr));
	bzero(&trans, sizeof(trans));
	bzero(&transe, sizeof(transe));

	transe[0].rs_num = PF_RULESET_FILTER;
	trans.size = 1;
	trans.esize = sizeof(transe[0]);
	trans.array = transe;
	ioctl(dev, DIOCXBEGIN, &trans);
	ioctl(dev, DIOCBEGINADDRS, &pp);

	pr.ticket = transe[0].ticket;
	pr.pool_ticket = pp.ticket;
	/* https://github.com/dotpy/py-pf/blob/master/pf/rule.py#L670 */

	/* block in */
	pr.rule.action = PF_DROP;
	pr.rule.direction = PF_IN;
	pr.rule.rtableid = -1;
	ioctl(dev, DIOCADDRULE, &pr);

	/* pass in on vtnet0 inet proto udp from any to any port > 1000 */
	pr.rule.action = PF_PASS;
	pr.rule.direction = PF_IN;
	strlcpy(pr.rule.ifname, IF, sizeof(pr.rule.ifname));
	pr.rule.af = AF_INET;
	pr.rule.proto = IPPROTO_UDP;
	pr.rule.dst.port[0] = htons(1000);
	pr.rule.dst.port_op = PF_OP_GT;

	ioctl(dev, DIOCADDRULE, &pr);

#if DEBUG
	/* pass in inet proto tcp from any to any port = ssh flags any keep state */
	pr.rule.max_src_states = 0;
	pr.rule.ifname[0] = '\0';
	bzero(& pr.rule.src.addr, sizeof (struct pf_addr));
	pr.rule.dst.port[0] = htons(22);
	pr.rule.dst.port_op = PF_OP_EQ;
	pr.rule.direction = PF_IN;
	pr.rule.action = PF_PASS;
	pr.rule.proto = IPPROTO_TCP;
	pr.rule.keep_state = PF_STATE_NORMAL;
	ioctl(dev, DIOCADDRULE, &pr);
#endif

	ioctl(dev, DIOCXCOMMIT, &trans);

	/* set tcp.finwait 5 */
	bzero(&pt, sizeof(pt));
	pt.seconds = 5;
	pt.timeout = PFTM_TCP_CLOSED;
	ioctl(dev, DIOCSETTIMEOUT, &pt);
	pt.seconds = 1;
	pt.timeout = PFTM_TCP_FIN_WAIT;
	ioctl(dev, DIOCSETTIMEOUT, &pt);

	close(dev);
}

int main(int argc, char *argv[])
{
	int status;

	setup();
	tableclear(true);
	launch_voteserver();
	launch_commserver();
	printf("launched\n");
	while (wait(&status) != -1) {
		printf("error\n");
	}
	return 0;
}
