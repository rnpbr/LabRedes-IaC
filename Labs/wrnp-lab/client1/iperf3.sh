# Comando para TCP
iperf3 -c 192.168.2.2 -t 1800 -i 1 -p 5102 -b 10G
# Comando para UDP
iperf3 -c 192.168.2.2 -t 600 -i 1 -u -b 10G -p 5103 &