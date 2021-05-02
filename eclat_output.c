#define HIKE_CHAIN_75_ID 75

#define HIKE_EBPF_PROG_PKT_MEM_MOVE 18
#include "eCLAT_Code/Code/Lib/Import/hike_program/pkt_mem_move.c"

#define HIKE_EBPF_PROG_GET_TIME_8_BIT 17
#include "eCLAT_Code/Code/Lib/Import/hike_program/get_time_8_bit.c"

#define HIKE_EBPF_PROG_GET_EXTERNAL_ID 16
#include "eCLAT_Code/Code/Lib/Import/hike_program/get_external_ID.c"

#define HIKE_EBPF_PROG_PKT_INTERFACE_LOAD 19
#include "eCLAT_Code/Code/Lib/Import/hike_program/interface_load.c"

HIKE_CHAIN_1(HIKE_CHAIN_75_ID) {
	__u16 eth_type;
	__u8 start_byte;
	__u8 mid_byte;
	__u8 end_byte;
	__u8 time;
	__u16 ex_id;
	__u8 load;
	hike_packet_read_u16(&eth_type, 12);
	if ( eth_type == 0x86dd ) {
		hike_packet_read_u8(&start_byte, 673);
		hike_packet_read_u8(&mid_byte, 681);
		hike_packet_read_u8(&end_byte, 689);
		if ( start_byte == 0x0 ) {
			if ( mid_byte == 0x0 ) {
				if ( end_byte == 0x0 ) {
					hike_elem_call_4(HIKE_EBPF_PROG_PKT_MEM_MOVE, 672, 361, 24);
					time = hike_elem_call_1(HIKE_EBPF_PROG_GET_TIME_8_BIT);
					ex_id = hike_elem_call_1(HIKE_EBPF_PROG_GET_EXTERNAL_ID);
					load = hike_elem_call_1(HIKE_EBPF_PROG_PKT_INTERFACE_LOAD);
					hike_packet_write_u8(361, time);
					hike_packet_write_u16(369, ex_id);
					hike_packet_write_u8(381, load);
				}
			}
		}
	}
	else {
		return -1;
	}

	return 0;
}
