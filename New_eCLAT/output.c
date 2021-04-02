#include <hike_vm.h>
#define MYCHAIN4 64
#define MYCHAIN5 65
#define __ETH_PROTO_TYPE_ABS_OFF 12
#define __IPV6_HOP_LIM_ABS_OFF 21
#define HIKE_EBPF_PROG_DROP_ANY 12
#define HIKE_EBPF_PROG_ALLOW_ANY 11

HIKE_CHAIN(MYCHAIN4) {
	__s64 allow, eth_type, hop_lim;
	allow = 1;
	hike_packet_read_u16(&eth_type, __ETH_PROTO_TYPE_ABS_OFF);
	if ( eth_type == 0x800 ) {
		allow = 0;
		hike_elem_call_3(MYCHAIN5, allow, eth_type);
	}
	if ( eth_type == 0x86dd ) {
		hike_packet_read_u16(&hop_lim, __IPV6_HOP_LIM_ABS_OFF);
		if ( hop_lim != 64 ) {
			hike_elem_call_3(MYCHAIN5, allow, eth_type);
		}
		hike_packet_write_u8(__ipv6_hop_lim_abs_off, 21);
	}
	return 0;
}

HIKE_CHAIN(MYCHAIN5, __s64 allow, __s64 eth_type) {
	__s64 prog_id;
	if ( allow == 1 ) {
		prog_id = hike_elem_call_1(HIKE_EBPF_PROG_ALLOW_ANY);
	}
	else {
		prog_id = hike_elem_call_1(HIKE_EBPF_PROG_DROP_ANY);
	}
	hike_elem_call_2(PROG_ID, eth_type);
	return 0;
}
