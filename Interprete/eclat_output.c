#define HIKE_CHAIN_MYCHAIN_ID 64
#define ENCAP_PROG_ID 0x0000f00l
#define MONITOR_PROG_ID 0x00008bad
#define ROUTING_PROG_ID 0x0000cafe
#define ENCAP_CONFIG 3
#define ENCAP_PARAM 1

HIKE_CHAIN(HIKE_CHAIN_MYCHAIN_ID) {
	__u16 ip_type;
	__u8 j;
	__u8 x;
	__u8 z;
	__u8 a;

	ip_type = 0xcafe;
	j =  ( 4 + 3 ) * 2 ;
	x =  4 +  3 * 2  ;
	if (  ( x + 2 ) + ( 1 + 1 )  == j ) {
		z = 3;
	}
	else {
		z = 2;
	}
	if (x < j) {
		a = 1;
	}
	if ( ( x + 5 ) > j ) {
		a = 4;
	}
	return 0;
}
