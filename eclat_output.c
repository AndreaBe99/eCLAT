#define HIKE_CHAIN_75_ID 75
#define HIKE_CHAIN_76_ID 76

#define HIKE_EBPF_PROG_DROP_ANY 12
#include "eCLAT_Code/Code/Lib/Import/hike_program/drop.c"

#define HIKE_EBPF_PROG_ALLOW_ANY 11
#include "eCLAT_Code/Code/Lib/Import/hike_program/allow.c"

#define __ETH_PROTO_TYPE_ABS_OFF 12

#define __IPV4_TOTAL_LEN_ABS_OFF 16

#define __IPV6_HOP_LIM_ABS_OFF 21

HIKE_CHAIN_1(HIKE_CHAIN_75_ID) {
	__u8 hop_lim;
	__u8 allow;
	__u16 ip4_len;
	__u16 eth_type;
	
	allow = 1;
	
	hike_packet_read_u16(&eth_type, __ETH_PROTO_TYPE_ABS_OFF);
	if ( eth_type == 0x800 ) {
		hike_packet_read_u16(&ip4_len, __IPV4_TOTAL_LEN_ABS_OFF);
		if ( ip4_len >= 128 ) {
			hike_elem_call_3(HIKE_CHAIN_76_ID, allow, eth_type);
			return 0;
		}
		allow = 0;
		hike_elem_call_3(HIKE_CHAIN_76_ID, allow, eth_type);
		return 0;
	}
	if ( eth_type == 0x86dd ) {
		hike_packet_read_u8(&hop_lim, __IPV6_HOP_LIM_ABS_OFF);
		if ( hop_lim != 64 ) {
			hike_elem_call_3(HIKE_CHAIN_76_ID, allow, eth_type);
			return 0;
		}
		hike_packet_write_u8(__IPV6_HOP_LIM_ABS_OFF, 17);
	}
	hike_elem_call_3(HIKE_CHAIN_76_ID, allow, eth_type);
	return 0;
	
}

HIKE_CHAIN_3(HIKE_CHAIN_76_ID, __u8, allow, __u16, eth_type) {
	__u32 prog_id;
	
	if ( allow == 1 ) {
		prog_id = HIKE_EBPF_PROG_ALLOW_ANY;
	}
	else {
		prog_id = HIKE_EBPF_PROG_DROP_ANY;
	}
	hike_elem_call_2(prog_id, eth_type);

	return 0;
}
