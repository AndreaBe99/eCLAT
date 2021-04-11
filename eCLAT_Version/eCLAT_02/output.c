#include <hike_vm.h>
#define HIKE_EBPF_PROG_DROP_ANY 12
#define HIKE_EBPF_PROG_ALLOW_ANY 11

__section("__sec_chain_mychain3")
int __chain_mychain3(void) {
	_s64 eth_type, a, b;
	eth_type = bpf_ntohs(__READ_PACKET(__be16, 12));
	a = 0;
	if ( a == 5 ) {
		b = 1;
	}
	else {
b = 2	}
	return XDP_ABORTED;
}
