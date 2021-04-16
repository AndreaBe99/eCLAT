#define HIKE_CHAIN_MYCHAIN1_ID 76
#define HIKE_CHAIN_MYCHAIN2_ID 77
#define HIKE_CHAIN_MYCHAIN5_ID 78
#define HIKE_EBPF_PROG_DROP_ANY 12
#define HIKE_EBPF_PROG_ALLOW_ANY 11
#define __ETH_PROTO_TYPE_ABS_OFF 12
#define __IPV6_HOP_LIM_ABS_OFF 21

HIKE_CHAIN(HIKE_CHAIN_MYCHAIN1_ID) {
	__u16 eth_type;
	__u8 hop_lim;

	hike_packet_read_u16(&eth_type, __ETH_PROTO_TYPE_ABS_OFF);
	if ( eth_type == 0x800 ) {
		hike_elem_call_2(HIKE_EBPF_PROG_DROP_ANY, eth_type);
		return 0;
	}
	if ( eth_type == 0x86dd ) {
		hike_packet_read_u8(&hop_lim, __IPV6_HOP_LIM_ABS_OFF);
		if (hop_lim != 64) {
			hike_elem_call_2(HIKE_EBPF_PROG_ALLOW_ANY, eth_type);
			return 0;
		}
		hike_packet_write_u8(__IPV6_HOP_LIM_ABS_OFF, 17);
	}
	return 0;
}

HIKE_CHAIN(HIKE_CHAIN_MYCHAIN2_ID) {
	__u8 allow;
	__u16 eth_type;
	__u8 hop_lim;

	allow = 1;
	hike_packet_read_u16(&eth_type, __ETH_PROTO_TYPE_ABS_OFF);
	if (eth_type == 0x800) {
		allow = 0;
		hike_elem_call_3(HIKE_CHAIN_MYCHAIN5_ID, allow, eth_type);
		return 0;
	}
	if (eth_type == 0x86dd) {
		hike_packet_read_u8(&hop_lim, __IPV6_HOP_LIM_ABS_OFF);
		if (hop_lim != 64) {
			hike_elem_call_3(HIKE_CHAIN_MYCHAIN5_ID, allow, eth_type);
			return 0;
		}
		hike_packet_write_u8(__IPV6_HOP_LIM_ABS_OFF, 17);
	}
	return 0;
}

HIKE_CHAIN(HIKE_CHAIN_MYCHAIN5_ID, __u8 allow, __u16 eth_type) {
	__u32 prog_id;

	if (allow == 1) {
		prog_id = hike_elem_call_1(HIKE_EBPF_PROG_ALLOW_ANY);
	}
	else {
		prog_id = hike_elem_call_1(HIKE_EBPF_PROG_DROP_ANY);
	}
	hike_elem_call_2(prog_id, eth_type);
	return 0;
}
