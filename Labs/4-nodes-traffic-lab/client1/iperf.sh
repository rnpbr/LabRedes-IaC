# Comando para TCP
iperf3 -c 192.168.2.2 -t 600 -i1 -P 5102 -p 5102 &

# Comando para UDP
iperf3 -c 192.168.2.2 -t 600 -i1 -P 5102 -u -b 1G -p 5103 &