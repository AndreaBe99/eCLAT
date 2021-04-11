#define HIKE_CHAIN_MYCHAIN_ID 64
#define ENCAP_PROG_ID 0x0000f00l
#define MONITOR_PROG_ID 0x00008bad
#define ROUTING_PROG_ID 0x0000cafe
#define ENCAP_CONFIG 3
#define ENCAP_PARAM 1

HIKE_CHAIN(HIKE_CHAIN_MYCHAIN_ID) {
	_u16 ip_type;
	_u8 j;
	_u8 x;
	_u8 z;
	_u8 a;
	_u8 b;
	_u8 c;
	_u8 d;

	ip_type = 0xcafe;
	j =  ( 4 + 3 ) * 2 ;
	x =  4 +  3 * 2  ;
	z =  5 >> 2 ;
	a =  5 >> 0x2 ;
	b =  5 << 2 ;
	c =  5 & 2 ;
	d =  5 | 2 ;
	return 0;
}
