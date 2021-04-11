#include <hike_vm.h>
#define MYCHAIN1 0
#define HIKE_EBPF_PROG_DROP_ANY 12
#define HIKE_EBPF_PROG_ALLOW_ANY 11

__section("__trp_chain_mychain1")
int __trp_chain_mychain1(void) {
	__s64 eth_type;
	__s64 ttl;

	eth_type = bpf_ntohs(__READ_PACKET(__be16, 12));
	if ( eth_type == 34525 ) {
		hike_call_2(HIKE_EBPF_PROG_DROP_ANY, eth_type);
		return XDP_ABORTED;
	}
	ttl = 64;
	if ( eth_type == 2048 ) {
		__WRITE_PACKET(__u8, ttl, 22);
	}
	hike_call_2(HIKE_EBPF_PROG_ALLOW_ANY, eth_type);
	return XDP_ABORTED;
}
