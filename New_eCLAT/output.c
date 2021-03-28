#include <hike_vm.h>
#define A 3
#define HIKE_EBPF_PROG_DROP_ANY 12
#define HIKE_EBPF_PROG_ALLOW_ANY 11

__section("__sec_chain_mychain3")
int __chain_mychain3(void) {
	_s64 eth_type, ttl;
	eth_type = bpf_ntohs(__READ_PACKET(__be16, 12));
	hike_elem_call_2(HIKE_EBPF_PROG_ALLOW_ANY, A);
	if ( eth_type == 34525 ) {
		ttl = bpf_ntohs(__READ_PACKET(__u8, 21));
		if ( ttl == 64 ) {
			__WRITE_PACKET(__u8, 21) = 17;
		}
		hike_elem_call_2(HIKE_EBPF_PROG_ALLOW_ANY, eth_type);
	}
	if ( eth_type == 2048 ) {
		hike_elem_call_2(HIKE_EBPF_PROG_DROP_ANY, eth_type);
	}
	return XDP_ABORTED;
}
