# NIC statistics

Those scripts can reach statistics of different cards and print current receive rate and drops.

- **card_stats.sh** - for Netcope 100G card to be used with watch(i.e. watch _./card_stats.sh_)
- **dpdk_pps.sh** - for Mellanox 100G card or 10G PRO models where DPDK is used. It needs also interface name as parametre (i.e. _./dpdk_pps.sh eth4_)
- **eth_pps.sh** - for any other interface card. It needs also interface name like the above one.
