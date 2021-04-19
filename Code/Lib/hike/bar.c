HIKE_PROG(bar)
{
    __u64 R0 = _I_REG(0);
    __u64 R1 = _I_REG(1);
    __u64 R2 = _I_REG(2);

    bpf_printk("HIKe Prog: bar REG_0=0x%llx, REG_1=0x%llx, REG_2=0x%llx", R0, R1, R2);

    return HIKE_XDP_VM;
}
EXPORT_HIKE_PROG(bar, HIKE_EBPF_PROG_BAR_ANY);