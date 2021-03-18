#define ENCAP_PROG_ID 0x0000f00l
#define MONITOR_PROG_ID 0x00008bad
#define ROUTING_PROG_ID 0x0000cafe
#define fast_no_kernel 1

__section("__trp_chain_myChain1")
int __trp_chain_myChain1(void) {

	__u64 a = hike_call_1(ENCAP_PROG_ID, 1);
	if ( a == 23 ) {
		hike_call_2(MONITOR_PROG_ID, 1, 2);
	}
	else {
		hike_call_1(ENCAP_PROG_ID, 1);
	}
	__u64 b = hike_call_1(ROUTING_PROG_ID, fast_no_kernel);
	if ( b == 21 ) {
		hike_call_0(FAKE_PROG_ID);
	}
	return XDP_DROP;
}

__section("__trp_chain_myChain3")
int __trp_chain_myChain3(void) {

	hike_call_1(ENCAP_PROG_ID, 1);
	return XDP_DROP;
}

__section("__trp_chain_myChain2")
int __trp_chain_myChain2(void) {

	__u64 a = 0;
	while ( a < 5 ) {
		hike_call_1(ENCAP_PROG_ID, a);
		hike_call_1(MONITOR_PROG_ID, 2);
		a =  a + 1 ;
		__u64 b = hike_call_1(ROUTING_PROG_ID, fast_no_kernel);
		if ( b == 21 ) {
			hike_call_1(FAKE_PROG_ID, 0);
		}
	}
	return XDP_DROP;
}
