#define HIKE_CHAIN_MYCHAIN_ID 76
#define ENCAP_PROG_ID 0x0000f00l
#define MONITOR_PROG_ID 0x00008bad
#define ROUTING_PROG_ID 0x0000cafe
#define ENCAP_CONFIG 3
#define ENCAP_PARAM 1

HIKE_CHAIN(HIKE_CHAIN_MYCHAIN_ID) {
	__u16 ip_type;
	__u8 a;

	ip_type = 0xcafe;
	if ( ENCAP_CONFIG == 3 ) {
		a = 2;
		if ( a == 2 ) {
			a = 3;
		}
		else {
			a = 250;
		}
	}
	return 0;
}
#define J  4 +  5 * 3  
#define Y  J * J 
