#include <hike_vm.h>
#define MYCHAIN2 64
#define HIKE_EBPF_PROG_DROP_ANY 12
#define HIKE_EBPF_PROG_ALLOW_ANY 11

HIKE_CHAIN(MYCHAIN2) {
	__s64 eth_type, ttl;
	hike_packet_read_u16(&eth_type, 12);
	if ( eth_type == 0x86dd ) {
		hike_elem_call_2(HIKE_EBPF_PROG_DROP_ANY, eth_type);
		return 0;
	}
	ttl = 64;
	if ( eth_type == 0x800 ) {
		hike_packet_write_u8(ttl, 22);
	}
	hike_elem_call_2(HIKE_EBPF_PROG_ALLOW_ANY, eth_type);
	return 0;
}
