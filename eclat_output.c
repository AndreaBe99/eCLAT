#define HIKE_CHAIN_75_ID 75
#define HIKE_CHAIN_76_ID 76
#define HIKE_CHAIN_77_ID 77
#define HIKE_CHAIN_78_ID 78
#define HIKE_CHAIN_79_ID 79

#define HIKE_EBPF_PROG_ALLOW_ANY 11
#include "eCLAT_Code/Code/Lib/Import/hike_program/allow.c"

#define HIKE_EBPF_PROG_MON 13
#include "eCLAT_Code/Code/Lib/Import/hike_program/mon.c"

#define HIKE_EBPF_PROG_SLOW 15
#include "eCLAT_Code/Code/Lib/Import/hike_program/slow.c"

#define HIKE_EBPF_PROG_FAST 14
#include "eCLAT_Code/Code/Lib/Import/hike_program/fast.c"

#define __OFFSET_TTL 64

HIKE_CHAIN_3(HIKE_CHAIN_75_ID, __s16, tos) {
	__u32 cnt;
	cnt = hike_elem_call_2(HIKE_EBPF_PROG_MON, tos);
	if ( cnt < 1000 ) {
		hike_elem_call_1(HIKE_EBPF_PROG_FAST);
	}
	else {
		hike_elem_call_1(HIKE_EBPF_PROG_SLOW);
	}
;
	return -1;
	
}

HIKE_CHAIN_3(HIKE_CHAIN_76_ID, __s16, tos) {
	hike_elem_call_2(HIKE_EBPF_PROG_MON, tos);
	hike_elem_call_1(HIKE_EBPF_PROG_SLOW);
	return -1;
	
}

HIKE_CHAIN_3(HIKE_CHAIN_77_ID, __s16, tos) {
	hike_packet_write_u8(__OFFSET_TTL, 10);
	hike_elem_call_2(HIKE_CHAIN_76_ID, tos);
	return -1;
	
}

HIKE_CHAIN_1(HIKE_CHAIN_78_ID) {
	__u16 eth_type;
	__s16 tos;
	hike_packet_read_u16(&eth_type, 12);
	tos = -1;
	if ( eth_type == 0x800 ) {
		hike_packet_read_u8(&tos, 16);
	}
	return tos;
	
}

HIKE_CHAIN_1(HIKE_CHAIN_79_ID) {
	__s16 tos;
	tos = hike_elem_call_1(HIKE_CHAIN_78_ID);
	if ( tos < 0 ) {
		hike_elem_call_1(HIKE_EBPF_PROG_SLOW);
		return -1;
	}
	if ( tos == 4 ) {
		hike_elem_call_2(HIKE_CHAIN_75_ID, tos);
	}
	else {
		if ( tos == 12 ) {
			hike_elem_call_2(HIKE_CHAIN_76_ID, tos);
		}
		else {
			if ( tos == 16 ) {
				hike_elem_call_2(HIKE_CHAIN_77_ID, tos);
			}
			else {
				if ( tos == 28 ) {
					hike_elem_call_1(HIKE_EBPF_PROG_FAST);
				}
				else {
					hike_elem_call_1(HIKE_EBPF_PROG_ALLOW_ANY);
				}

			}
		}
	}
	return -1;
	
}
