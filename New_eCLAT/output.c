#include <hike_vm.h>
#define HIKE_EBPF_PROG_DROP_ANY 12
#define HIKE_EBPF_PROG_ALLOW_ANY 11

__section("__sec_chain_mychain2")
int __chain_mychain2(void) {
	_s64 eth_type, ttl;
	eth_type = bpf_ntohs(__READ_PACKET(__be16, 12));
	if ( eth_type == 0x86dd ) {
		hike_elem_call_2(HIKE_EBPF_PROG_DROP_ANY, eth_type);
		return XDP_ABORTED;
	}
	ttl = 64;
	if ( eth_type == 0x800 ) {
		__WRITE_PACKET(__u8, 22) = ttl;
	}
	hike_elem_call_2(HIKE_EBPF_PROG_ALLOW_ANY, eth_type);
	return XDP_ABORTED;
}
