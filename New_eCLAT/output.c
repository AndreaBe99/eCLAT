#define ENCAP_PROG_ID 0x0000f00l
#define MONITOR_PROG_ID 0x00008bad
#define ROUTING_PROG_ID 0x0000cafe
#define FAST_NO_KERNEL 1

__section("__trp_chain_myChain1")
int __trp_chain_myChain1(void) {
	__u64 a;
	__u64 b;

	a = hike_call_1(ENCAP_PROG_ID, 1);
	if ( a == 23 ) {
		hike_call_1(MONITOR_PROG_ID, 2);
	}
	b = hike_call_1(ROUTING_PROG_ID, FAST_NO_KERNEL);
	if ( b == 21 ) {
		hike_call_1(FAKE_PROG_ID, 0);
	}
	return a;
	
}

__section("__trp_chain_myChain2")
int __trp_chain_myChain2(void) {
	__u64 a;

	a = hike_call_1(ENCAP_PROG_ID, 1);
	__u64 a;
	__u64 b;

	a = hike_call_1(ENCAP_PROG_ID, 1);
	if ( a == 23 ) {
		hike_call_1(MONITOR_PROG_ID, 2);
	}
	b = hike_call_1(ROUTING_PROG_ID, FAST_NO_KERNEL);
	if ( b == 21 ) {
		hike_call_1(FAKE_PROG_ID, 0);
	}
	return a;
	return XDP_DROP;
}
