#define HIKE_CHAIN_75_ID 75

#define HIKE_EBPF_PROG_PKT_MEM_MOVE 18
#include "eCLAT_Code/Code/Lib/Import/hike_program/pkt_mem_move.c"

#define HIKE_EBPF_PROG_GET_TIME_8_BIT 17
#include "eCLAT_Code/Code/Lib/Import/hike_program/get_time_8_bit.c"

#define HIKE_EBPF_PROG_GET_EXTERNAL_ID 16
#include "eCLAT_Code/Code/Lib/Import/hike_program/get_external_ID.c"

#define HIKE_EBPF_PROG_PKT_INTERFACE_LOAD 19
#include "eCLAT_Code/Code/Lib/Import/hike_program/interface_load.c"

#define __IPV6_START_39_BYTE_OFF 673

#define __IPV6_MID_40_BYTE_OFF 681

#define __IPV6_END_41_BYTE_OFF 689

#define __IPV6_CMD_TTS_OFF 361

#define __IPV6_CMD_OIF_OFF 369

#define __IPV6_CMD_OIL_OFF 381

HIKE_CHAIN_1(HIKE_CHAIN_75_ID) {
	__u16 eth_type;
	__u8 start_byte;
	__u8 mid_byte;
	__u8 end_byte;
	__u8 time;
	__u16 ex_id;
	__u8 in_load;
	hike_packet_read_u16(&eth_type, 12);
	if ( eth_type == 0x86dd ) {
		hike_packet_read_u8(&start_byte, __IPV6_START_39_BYTE_OFF);
		hike_packet_read_u8(&mid_byte, __IPV6_MID_40_BYTE_OFF);
		hike_packet_read_u8(&end_byte, __IPV6_END_41_BYTE_OFF);
		if ( start_byte == 0x0 ) {
			if ( mid_byte == 0x0 ) {
				if ( end_byte == 0x0 ) {
					hike_elem_call_4(HIKE_EBPF_PROG_PKT_MEM_MOVE, 672, 361, 24);
					time = hike_elem_call_1(HIKE_EBPF_PROG_GET_TIME_8_BIT);
					ex_id = hike_elem_call_1(HIKE_EBPF_PROG_GET_EXTERNAL_ID);
					in_load = hike_elem_call_1(HIKE_EBPF_PROG_PKT_INTERFACE_LOAD);
					hike_packet_write_u8(__IPV6_CMD_TTS_OFF, time);
					hike_packet_write_u16(__IPV6_CMD_OIF_OFF, ex_id);
					hike_packet_write_u8(__IPV6_CMD_OIL_OFF, in_load);
				}
			}
		}
	}
	else {
		return -1;
	}

	return 0;
}
