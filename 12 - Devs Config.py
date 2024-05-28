Project 12  - Complete Campus Area Network - Devs Configuration

### ROUTERS ###

## ALL ROUTERS ##

En
Conf t

exit
do wr

## HQ-Airtel-ISP ##

En
Conf t
hostname HQ-Airtel-ISP

int gi0/0
no shut
ip address 105.100.50.1 255.255.255.252
exit

int se0/3/0
no shut
clock rate 64000
ip address 20.20.20.2 255.255.255.252
exit

//OSPF
router ospf 15
auto-cost reference-bandwidth 100000
router-id 7.7.7.7
network 105.100.50.0 0.0.0.3 area 0
network 20.20.20.0 0.0.0.3 area 0
exit

do wr

## Branch-Airtel-ISP ##

En
Conf t
hostname BRanch-Airtel-ISP

int se0/3/0
no shut
ip address 30.30.30.2 255.255.255.252
exit

int gi0/1
no shut
ip address 205.200.100.1 255.255.255.252
exit

//OSPF

router ospf 15
auto-cost reference-bandwidth 100000
router-id 9.9.9.9
network 30.30.30.0 0.0.0.3 area 0
network 205.200.100.0 0.0.0.3 area 0
exit

do wr

## Internet ##

En
Conf t
hostname Internet-Router

int se0/3/0
no shut
ip address 20.20.20.1 255.255.255.252
exit

int gi0/2
no shut
ip address 8.0.0.1 255.0.0.2
exit

int se0/3/1
no shut
clock rate 64000
ip address 30.30.30.1 255.255.255.252
exit

//OSPF
router ospf 15
auto-cost reference-bandwidth 100000
router-id 8.8.8.8
network 20.20.20.0 0.0.0.3 area 0
network 8.0.0.0 0.255.255.255 area 0
network	30.30.30.0 0.0.0.3 area 0
exit

do wr

### FIREWALLS ###

## ALL FIREWALLS ##

En
Conf t

exit
do wr

## HQ-FW ##

En
Conf t
hostname HQ-FW

int gi1/1
no shut
nameif INSIDE1
security-level 100
ip address 10.20.20.34 255.255.255.252
exit

int gi1/2
no shut
nameif INSIDE2
security-level 100
ip address 10.20.20.38 255.255.255.252
exit

int gi1/3
no shut
nameif OUTSIDE
security-level 0
ip address 105.100.50.2 255.255.255.252
exit

int gi1/4
no shut
nameif DMZ
security-level 70
ip address 10.20.20.1 255.255.255.224
exit

//OSPF

router ospf 15
router-id 5.5.5.5
network 10.20.20.0 255.255.255.224 area 0
network 105.100.50.0 255.255.255.252 area 0
network 10.20.20.32 255.255.255.252 area 0
network 10.20.20.36 255.255.255.252 area 0
exit 

// Default static route if any packet from HQ network
// Does not go to that network

route OUTSIDE 0.0.0.0 0.0.0.0 105.100.50.1

//PAT - ref: NAT(applied-from, applied-to)

object network MGMT-INSIDE1-OUTSIDE
subnet 192.168.10.0 255.255.255.0
nat (INSIDE1,OUTSIDE) dynamic interface

object network MGMT-INSIDE2-OUTSIDE
subnet 192.168.10.0 255.255.255.0
nat (INSIDE2,OUTSIDE) dynamic interface

object network LAN-INSIDE1-OUTSIDE
subnet 172.16.0.0 255.255.0.0
nat (INSIDE1,OUTSIDE) dynamic interface

object network LAN-INSIDE2-OUTSIDE
subnet 172.16.0.0 255.255.0.0
nat (INSIDE2,OUTSIDE) dynamic interface

object network WLAN-INSIDE1-OUTSIDE
subnet 10.10.0.0 255.255.0.0
nat (INSIDE1,OUTSIDE) dynamic interface

object network WLAN-INSIDE2-OUTSIDE
subnet 10.10.0.0 255.255.0.0
nat (INSIDE2,OUTSIDE) dynamic interface
exit

//Basic inspection policies through extended ACLs
//Ports: DHCP -> UDP 67,68. DNS-> UDP 53, TCP53. FTP-> TCP 20,21
	     EMAIL: SMTP(enc)-> UDP 465, POP3(enc)->UDP 995, IMAP(enc)->UDP 993
	     CAPWAP: UDP 5246,5247,12222,12223
	     
conf t
access-list resources-access extended permit icmp any any
access-list resources-access extended permit udp any any eq 67
access-list resources-access extended permit udp any any eq 68
access-list resources-access extended permit udp any any eq 53
access-list resources-access extended permit tcp any any eq 53
access-list resources-access extended permit tcp any any eq 80
access-list resources-access extended permit tcp any any eq 443
access-list resources-access extended permit udp any any eq 465
access-list resources-access extended permit udp any any eq 995
access-list resources-access extended permit udp any any eq 993
access-list resources-access extended permit tcp any any eq 20
access-list resources-access extended permit tcp any any eq 21
access-list resources-access extended permit udp any any eq 5246
access-list resources-access extended permit udp any any eq 5247
access-list resources-access extended permit udp any any eq 12222
access-list resources-access extended permit udp any any eq 12223

access-group resources-access in interface DMZ
access-group resources-access in interface OUTSIDE
exit


//IPSec Tunnel

conf t
crypto ikev1 policy 10
hash sha
authentication pre-share

group 2
lifetime 86400
encryption 3des
exit

tunnel-group 205.200.100.2 type ipsec-l2l
tunnel-group 205.200.100.2 ipsec-attributes
ikev1 pre-shared-key cisco
exit

crypto ipsec ikev1 transform-set TSET esp-3des esp-sha-hmac

access-list VPN-ACL permit ip 192.168.10.0 255.255.255.0 172.17.0.0 255.255.0.0
access-list VPN-ACL permit ip 192.168.10.0 255.255.255.0 10.11.0.0 255.255.0.0

access-list VPN-ACL permit ip 172.16.0.0 255.255.0.0 172.17.0.0 255.255.0.0
access-list VPN-ACL permit ip 172.16.0.0 255.255.0.0 10.11.0.0 255.255.0.0

access-list VPN-ACL permit ip 10.10.0.0 255.255.0.0 172.17.0.0 255.255.0.0
access-list VPN-ACL permit ip 10.10.0.0 255.255.0.0 10.11.0.0 255.255.0.0

access-list VPN-ACL permit ip 10.20.20.0 255.255.255.224 172.17.0.0 255.255.0.0
access-list VPN-ACL permit ip 10.20.20.0 255.255.255.224 10.11.0.0 255.255.0.0

crypto map CMAP 10 set peer 205.200.100.2
crypto map CMAP 10 set ikev1 transform-set TSET
Crypto map CMAP 10 match address VPN-ACL

crypto map CMAP interface OUTSIDE
crypto ikev1 enable OUTSIDE

wr mem

## Branch-FW ##

En
Conf t
hostname Branch-FW

int gi1/1
no shut
nameif INSIDE1
security-level 100
ip address 10.20.20.42 255.255.255.252
exit

int gi1/2
no shut
nameif INSIDE2
security-level 100
ip address 10.20.20.46 255.255.255.252
exit

int gi1/3
no shut
nameif OUTSIDE
security-level 0
ip address 205.200.100.2 255.255.255.252
exit

//OSPF
router ospf 15
router-id 6.6.6.6
network 205.200.100.0 255.255.255.252 area 0
network 10.20.20.40 255.255.255.252 area 0
network 10.20.20.44 255.255.255.252 area 0
exit

// Default static route if any packet from HQ network
// Does not go to that network

route OUTSIDE 0.0.0.0 0.0.0.0 205.200.100.1

//PAT - ref: NAT(applied-from, applied-to)

object network LAN-INSIDE1-OUTSIDE
subnet 172.17.0.0 255.255.0.0
nat (INSIDE1,OUTSIDE) dynamic interface

object network LAN-INSIDE2-OUTSIDE
subnet 172.17.0.0 255.255.0.0
nat (INSIDE2,OUTSIDE) dynamic interface

object network WLAN-INSIDE1-OUTSIDE
subnet 10.11.0.0 255.255.0.0
nat (INSIDE1,OUTSIDE) dynamic interface

object network WLAN-INSIDE2-OUTSIDE
subnet 10.11.0.0 255.255.0.0
nat (INSIDE2,OUTSIDE) dynamic interface
exit

//Basic inspection policies through extended ACLs
//Ports: DHCP -> UDP 67,68. DNS-> UDP 53, TCP53. FTP-> TCP 20,21
	     EMAIL: SMTP(enc)-> UDP 465, POP3(enc)->UDP 995, IMAP(enc)->UDP 993
	     CAPWAP: UDP 5246,5247,12222,12223

conf t
access-list resources-access extended permit icmp any any
access-list resources-access extended permit udp any any eq 67
access-list resources-access extended permit udp any any eq 68
access-list resources-access extended permit udp any any eq 53
access-list resources-access extended permit tcp any any eq 53
access-list resources-access extended permit tcp any any eq 80
access-list resources-access extended permit tcp any any eq 443
access-list resources-access extended permit udp any any eq 465
access-list resources-access extended permit udp any any eq 995
access-list resources-access extended permit udp any any eq 993
access-list resources-access extended permit tcp any any eq 20
access-list resources-access extended permit tcp any any eq 21
access-list resources-access extended permit udp any any eq 5246
access-list resources-access extended permit udp any any eq 5247
access-list resources-access extended permit udp any any eq 12222
access-list resources-access extended permit udp any any eq 12223

access-group resources-access in interface OUTSIDE
exit

//IPSec Tunnel

conf t
crypto ikev1 policy 10
hash sha
authentication pre-share

group 2
lifetime 86400
encryption 3des
exit

tunnel-group 105.100.50.2 type ipsec-l2l
tunnel-group 105.100.50.2 ipsec-attributes
ikev1 pre-shared-key cisco
exit

crypto ipsec ikev1 transform-set TSET esp-3des esp-sha-hmac

access-list VPN-ACL permit ip 172.17.0.0 255.255.0.0 192.168.10.0 255.255.255.0 
access-list VPN-ACL permit ip 172.17.0.0 255.255.0.0 172.16.0.0 255.255.0.0 
access-list VPN-ACL permit ip 172.17.0.0 255.255.0.0 10.10.0.0 255.255.0.0 
access-list VPN-ACL permit ip 172.17.0.0 255.255.0.0 10.20.20.0 255.255.255.224

access-list VPN-ACL permit ip 10.11.0.0 255.255.0.0 192.168.10.0 255.255.255.0 
access-list VPN-ACL permit ip 10.11.0.0 255.255.0.0 172.16.0.0 255.255.0.0 
access-list VPN-ACL permit ip 10.11.0.0 255.255.0.0 10.10.0.0 255.255.0.0 
access-list VPN-ACL permit ip 10.11.0.0 255.255.0.0 10.20.20.0 255.255.255.224 


crypto map CMAP 10 set peer 105.100.50.2
crypto map CMAP 10 set ikev1 transform-set TSET
crypto map CMAP 10 match address VPN-ACL

crypto map CMAP interface OUTSIDE
crypto ikev1 enable OUTSIDE

wr mem

### ALL L3 SWITCHES ###

//Basic configs 

En
Conf t
Banner motd **UNAUTHORIZED ACCESS IS PUNISHABLE**
Line console 0
Password cisco
Login
exec-timeout 3 0
Enable password cisco
No ip domain-lookup
Service password-encryption
Ip domain-name cisco.com
Username cisco password cisco
Crypto key generate rsa general-keys modulus 1024
Ip ssh version 2

// ACL for SSH only authorized access from MGMT network

access-list 2 permit 192.168.10.0 255.255.255.0
access-list 2 deny any
line vty 0 15
login local
transport input ssh
access-class 2 in
exit

Do wr

## HQ-L3-SW1 ##

En
Conf t
hostname HQ-L3-SW1

vlan 10
name Management
vlan 20
name LAN
vlan 50
name WLAN
vlan 99
name Native
vlan 199
name Blackhole
exit

int ran gi1/0/2-6
no shut
switchport mode trunk
switchpor trunk native vlan 99
exit

//if connected to WLC
int gi1/0/10
no shut
switchport mode access
switchport access vlan 50
spanning-tree portfast
spanning-tree bpduguard enable
exit

//HSRP - Avtive
int ran gi1/0/7-9
no shut
channel-group 1 mode active
switchport mode trunk
exit

int vlan 10
ip address 192.168.10.3 255.255.255.0
ip helper-address 10.20.20.5
ip helper-address 10.20.20.6
standby 10 ip 192.168.10.1
exit

int vlan 20
ip address 172.16.0.3 255.255.0.0
ip helper-address 10.20.20.5
ip helper-address 10.20.20.6
standby 20 ip 172.16.0.1
exit

int vlan 50
ip address 10.10.0.3 255.255.0.0
ip helper-address 10.20.20.5
ip helper-address 10.20.20.6
standby 50 ip 10.10.0.1
exit

int gi1/0/1
no shut
no switchport
ip address 10.20.20.33 255.255.255.252
exit

//OSPF
ip routing
router ospf 15
auto-cost reference-bandwidth 100000
router-id 1.1.1.1
network 10.20.20.32 0.0.0.3 area 0
network 192.168.10.0 0.0.0.255 area 0
network 172.16.0.0 0.0.255.255 area 0
network 10.10.0.0 0.0.255.255 area 0
exit

do wr

## HQ-L3-SW2 ##

En
Conf t
Hostname HQ-L3-SW2

vlan 10
name Management
vlan 20
name LAN
vlan 50
name WLAN
vlan 99
name Native
vlan 199
name Blackhole
exit

int ran gi1/0/2-6
no shut
switchport mode trunk
switchpor trunk native vlan 99
exit

//HSRP - Passive

int ran gi1/0/7-9
no shut
channel-group 1 mode passive
switchport mode trunk
exit

int vlan 10
ip address 192.168.10.2 255.255.255.0
ip helper-address 10.20.20.5
ip helper-address 10.20.20.6
standby 10 ip 192.168.10.1
exit

int vlan 20
ip address 172.16.0.2 255.255.0.0
ip helper-address 10.20.20.5
ip helper-address 10.20.20.6
standby 20 ip 172.16.0.1
exit

int vlan 50
ip address 10.10.0.2 255.255.0.0
ip helper-address 10.20.20.5
ip helper-address 10.20.20.6
standby 50 ip 10.10.0.1
exit

int gi1/0/1
no shut
no switchport
ip address 10.20.20.37 255.255.255.252
exit

//OSPF
ip routing
router ospf 15
auto-cost reference-bandwidth 100000
router-id 2.2.2.2
network 10.20.20.36 0.0.0.3 area 0
network 192.168.10.0 0.0.0.255 area 0
network 172.16.0.0 0.0.255.255 area 0
network 10.10.0.0 0.0.255.255 area 0

exit
do wr

## BRANCH-L3-SW1 ##

En
Conf t
hostname Branch-L3-SW1

vlan 60
name Branch-LAN
vlan 90
name Branch-WLAN
vlan 99
name native
vlan 199
name Blackhole
exit

int ran gi1/0/2-5
no shut
switchport mode trunk
switchport trunk native vlan 99
exit

//HSRP - Active
int ran gi1/0/6-8
no shut
channel-group 2 mode active
switchport mode trunk
exit

int vlan 60
ip address 172.17.0.3 255.255.0.0
ip helper-address 10.20.20.5
ip helper-address 10.20.20.6
standby 60 ip 172.17.0.1
exit

int vlan 90
ip address 10.11.0.3 255.255.0.0
ip helper-address 10.20.20.5
ip helper-address 10.20.20.6
standby 90 ip 10.11.0.1
exit

int gi1/0/1
no shut
no switchport
ip address 10.20.20.41 255.255.255.252
exit

//OSPF
ip routing
router ospf 15
auto-cost reference-bandwidth 100000
router-id 3.3.3.3
network 10.20.20.40 0.0.0.3 area 0
network 172.17.0.0 0.0.255.255 area 0
network 10.11.0.0 0.0.255.255 area 0
exit

do wr

## BRANCH-L3-SW2 ##

En
Conf t
hostname Branch-L3-SW2

vlan 60
name Branch-LAN
vlan 90
name Branch-WLAN
vlan 99
name native
vlan 199
name Blackhole
exit

int ran gi1/0/2-5
no shut
switchport mode trunk
switchport trunk native vlan 99
exit

//HSRP - Passive

int ran gi1/0/6-8
no shut
channel-group 2 mode passive
switchport mode trunk
exit

int vlan 60
ip address 172.17.0.2 255.255.0.0
ip helper-address 10.20.20.5
ip helper-address 10.20.20.6
standby 60 ip 172.17.0.1
exit

int vlan 90
ip address 10.11.0.2 255.255.0.0
ip helper-address 10.20.20.5
ip helper-address 10.20.20.6
standby 90 ip 10.11.0.1
exit

int gi1/0/1
no shut
no switchport
ip address 10.20.20.45 255.255.255.252
exit

//OSPF
ip routing
router ospf 15
auto-cost reference-bandwidth 100000
router-id 4.4.4.4
network 10.20.20.44 0.0.0.3 area 0
network 172.17.0.0 0.0.255.255 area 0
network 10.11.0.0 0.0.255.255 area 0

exit
do wr

### SWITCHES ###

## ALL HQ SWITCHES ##

//Basic configs 

En
Conf t
Banner motd **UNAUTHORIZED ACCESS IS PUNISHABLE**
Line console 0
Password cisco
Login
exec-timeout 3 0
Enable password cisco
No ip domain-lookup
Service password-encryption
Ip domain-name cisco.com
Username cisco password cisco
Crypto key generate rsa general-keys modulus 1024
Ip ssh version 2

// ACL for SSH only authorized access from MGMT network

access-list 2 permit 192.168.10.0 255.255.255.0
access-list 2 deny any
line vty 0 15
login local
transport input ssh
access-class 2 in
exit

vlan 10
name Management
vlan 20
name LAN
vlan 50
name WLAN
vlan 99
name Native
vlan 199
name Blackhole
exit

int ran gi0/1-2
no shut
switchport mode trunk
switchport trunk native vlan 99
exit

int ran fa0/1-14
no shut
switchport mode access
switchport access vlan 20
exit

int ran fa0/15-20
switchport mode access
switchport access vlan 199
shut
exit

int ran fa0/21-24
no shut
switchport mode	access
switchport access vlan 50
exit

int ran fa0/1-24
spanning-tree portfast
spanning-tree bpduguard enable
exit

Do wr

## H&S-SW ##

En
Conf t
hostname H&S-SW

exit
do wr

## BUS-SW ##

En
Conf t
hostname BUS-SW

exit
do wr

## ENG&COM-SW ##

En
Conf t
hostname ENG&COM-SW

exit
do wr

## ART&DES-SW ##

En
Conf t
hostname ART&DES-SW

exit
do wr

## IT-SW ##

En
Conf t
hostname IT-SW

int ran fa0/15-17
no shut
switchport mode access
no switchport access vlan 199
switchport access vlan 10
exit

do wr

## DMZ-SW ##

En
Conf t
hostname DMZ-SW

int ran fa0/1-24
spanning-tree portfast
spanning-tree bpduguard enable
exit

do wr

## ALL BRANCH SWITCHES ##

//Basic configs 

En
Conf t
Banner motd **UNAUTHORIZED ACCESS IS PUNISHABLE**
Line console 0
Password cisco
Login
exec-timeout 3 0
Enable password cisco
No ip domain-lookup
Service password-encryption
Ip domain-name cisco.com
Username cisco password cisco
Crypto key generate rsa general-keys modulus 1024
Ip ssh version 2

// ACL for SSH only authorized access from MGMT network

access-list 2 permit 192.168.10.0 255.255.255.0
access-list 2 deny any
line vty 0 15
login local
transport input ssh
access-class 2 in
exit

vlan 60
name LAN
vlan 90
name WLAN
vlan 99
name Native
vlan 199
name Blackhole
exit

int ran gi0/1-2
no shut
switchport mode trunk
switchport trunk native vlan 99
exit

int ran fa0/1-14
no shut
switchport mode access
switchport access vlan 60
exit

int ran fa0/15-20
no shut
switchport mode access
switchport access vlan 199
exit

int ran fa0/21-24
no shut
switchport mode access
switchport access vlan 90
exit

do wr

## Branch-H&S-SW ##

En
Conf t
hostname Branch-H&S-SW

exit
do wr

## Branch-BUS-SW ##

En
Conf t
hostname Branch-BUS-SW

exit
do wr

## Branch-ART&DES-SW ##

En
Conf t
hostname Branch-ART&DES-SW

exit
do wr

## Branch-IT-SW ##

En
Conf t
hostname Branch-IT-SW

exit
do wr