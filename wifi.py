#!/usr/bin/env python

import subprocess
import sys

def execute(cmd):
    Command=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
    (out, err)=Command.communicate()
    if err:
        print(err)
        exit(1)
    return out

if len(sys.argv)<=2 :
    print('Arguments : interface  , ESSID , [ mac address ] ')
    exit(1)
else :
    interface = sys.argv[1]
    ESSID = sys.argv[2]
    mac = '00:00:00:00:00:66'

leases_file = '/var/lib/dhclient/dhclient.leases'  

# connecting to wifi and setting up mac

execute('ifconfig ' + interface  + ' down')
execute('ifconfig ' + interface  + ' hw ether ' + mac + ' up')
execute('iwconfig ' +  interface + ' ESSID ' + ESSID )

# checking gor wifi connectivity
out = execute('iwconfig '+  interface + ' | grep LINK')
if len(out) == 0:
    print('Wifi could not be reached ')


# killing dhclient
try:
    execute('dhclient -r ' + interface)
    execute('killall dhclient ')
except:
    print('killed dhclient')

# taking a dynamic ip to get info about all open ip
execute('dhclient ' + interface)

gateway = execute('grep routers ' + leases_file).split('\n')[-2].split()[-1][:-1]
print(gateway)

# our interface ip assigned using dhcp
my_ip = execute('ifconfig ' +  interface + ' | grep -w inet').split()[1]

# calculation of network , netmask , broadcast and available ip addresses

interface_info = execute('ifconfig ' + interface + ' | grep inet').split()

netmask = interface_info[3]
bin_net = bin(int(netmask.split('.')[0]))[2:].zfill(8) + bin(int(netmask.split('.')[1]))[2:].zfill(8) + bin(int(netmask.split('.')[2]))[2:].zfill(8) + bin(int(netmask.split('.')[3]))[2:].zfill(8)
mask = bin_net.count('1')
print('netmask  ',netmask)

broadcast = interface_info[5]
bin_broadcast = bin(int(broadcast.split('.')[0]))[2:].zfill(8) + bin(int(broadcast.split('.')[1]))[2:].zfill(8) + bin(int(broadcast.split('.')[2]))[2:].zfill(8) + bin(int(broadcast.split('.')[3]))[2:].zfill(8)
print('broadcast',broadcast)

ip = interface_info[1]
bin_ip = bin(int(ip.split('.')[0]))[2:].zfill(8) + bin(int(ip.split('.')[1]))[2:].zfill(8) + bin(int(ip.split('.')[2]))[2:].zfill(8) + bin(int(ip.split('.')[3]))[2:].zfill(8)
print('ip',ip)

super = pow(2,32) - 1
num_ip = super - int(bin_net,2)
print(num_ip)

num_network = int(bin_broadcast,2) - num_ip
bin_network = bin(num_network)[2:].zfill(32)
act_network = str(int(bin_network[:8],2)) + '.' + str(int(bin_network[8:16],2)) + '.' +str(int(bin_network[16:24],2)) + '.' +str(int(bin_network[24:],2))

list = []

for i in range(num_ip):
    addr = num_network + i + 1
    bin_addr = bin(addr)[2:].zfill(32)
    ip_addr = str(int(bin_addr[:8],2)) + '.' + str(int(bin_addr[8:16],2)) + '.' +str(int(bin_addr[16:24],2)) + '.' +str(int(bin_addr[24:],2))
    list.append(ip_addr)

# list contains all the ip to check from the current network
#print(list)

print("nmap -n -sn  " + act_network + '/' + str(mask) + " -oG - | awk '/Up$/{print $2}'")
ip_string = execute("nmap -n -sn  " + act_network + '/' + str(mask) + " -oG - | awk '/Up$/{print $2}'")
list_up = ip_string.split('\n')[:-1]

free_ip =[]

for ip in list:
   try:
       list_up.index(ip)
   except ValueError:
       free_ip.append(ip)


# uncomment this if u want to check from manual ip address space

#for i in range(4):
#    oct = '10.10.' + str(48 + i)
#    for j in range(255):
#        ip = oct +'.' + str(j + 1)
#        if ip != '10.10.51.255':
#            try:
#                list_up.index(ip)
#                #print(ip + " this can't be assigned \n")
#            except ValueError :
#                free_ip.append(ip)

print(len(free_ip))

# creating a new file
file = open('open_ips','w')
file.close()

for ipaddress in free_ip:
    execute('ifconfig ' + interface + ' ' + ipaddress + ' netmask ' + netmask)
    out = execute('ping ' + gateway  +' -c 1 -W 1 | grep ttl ')
    if len(out) == 0 :
        print("can't ping gateway with " + ipaddress)
        execute('iwconfig ' + interface + ' ESSID ' + ESSID)
        out = execute('ping ' + gateway  +' -c 1 -W 1 | grep ttl ')
    if out:
        execute('route add default gw ' + gateway)
        execute("echo -e 'nameserver 8.8.8.8'>> /etc/resolv.conf")
        out = execute("ping 8.8.8.8 -c 1 -W 1 | grep ttl ")
        if out:
            out = execute('curl --silent http://www.torrentz.eu/ | grep -e User -e Group')   # web site that should be blocked on your network
            file = open('open_ips','a')
            try:
                print(out.split('\n')[0] + '  ' + out.split('\n')[1] + '  ' + ipaddress)
                file.write(out.split('\n')[0] + '  ' + out.split('\n')[1] + '  ' + ipaddress + '\n')
            except IndexError:
                print('unblocked ip ' + ipaddress )
                file.write('unblocked ip ' + ipaddress + '\n')
            file.close()
        else:
            print(ipaddress + ' is free but not with authenication')


