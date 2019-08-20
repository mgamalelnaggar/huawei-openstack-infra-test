import paramiko
import time
import os
import platform
import re
import root_pswd_blades


################	Initialization		########################################
set_ifc_description = True
change_ipmi_address = False
change_root_password = False

### OoB switch credintials
'''
You should be able to reach OoB switch to manage it 10.x.x.x and also have another IP address 192.168.2.101
Use Win IP Config or any other program to have two IPs on your Eth NIC interface
'''
oob_sw_ip='10.55.48.1'
oob_sw_username='eventum'
oob_sw_password='P@ssw0rd123'

### iBMC credintials

# default ip address of the ibmc interface of the Rack servers
default_initial_ip='192.168.2.100'
default_initial_password='Huawei12#$'
new_root_password='Orange@2019'

### IPMI parameters

# Ipmi subnetmask
subnetmask='255.255.255.128'

# Ipmi network gateway
gateway='10.55.48.1'

# file contains ip,port number on OoB switch
info_file = "01-info_file.txt"
####################	Initialization End		################################

def ping_host(ip_add):
	hostname = ip_add #example
	param = '-n' if platform.system().lower()=='windows' else '-c'
	response = os.system("ping " + param + " 1 " + ip_add)
	x=10
	#and then check the response...
	while response != 0 and x>0:
		print ip_add, ' unreachable'
		response = os.system("ping " + param + " 1 " + ip_add)
		x=x-1
		time.sleep(2)
	else:
		if x==0:
			print ip_add, 'unreachable'
			return False
#			quit()
		else:
			print ip_add, 'reached!'
			return True

def change_ipmi_ip(ip,submask=subnetmask,default_ip=default_initial_ip,default_pass=default_initial_password):
	try:
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(default_ip, username='root', password=default_pass, look_for_keys=False, allow_agent=False)
		remote_conn = client.invoke_shell()
		time.sleep(3)

		remote_conn.send('ipmcset -d ipmode -v static')
		remote_conn.send('\n')
		time.sleep(2)

		remote_conn.send('ipmcset -d ipaddr -v ')
		remote_conn.send(ip)
		remote_conn.send(' ')
		remote_conn.send(submask)
		remote_conn.send(' ')
		remote_conn.send(gateway)
		remote_conn.send('\n')
		time.sleep(2)

		output = remote_conn.recv(65535)
		print output
		remote_conn.close()
		client.close()
		time.sleep(5)
		return ping_host(ip)
	except:
		print "Changing IPMI IP to %s failed" %ip

def change_password(ip,default_pass=default_initial_password,root_pass=new_root_password):
	try:
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(ip, username='root', password=default_pass, look_for_keys=False, allow_agent=False)
		remote_conn = client.invoke_shell()

		remote_conn.send('ipmcset -d password -v root')
		remote_conn.send('\n')
		time.sleep(5)
		output = remote_conn.recv(65535)
		print output

		remote_conn.send(default_pass)
		remote_conn.send('\n')
		time.sleep(2)
		output = remote_conn.recv(65535)
		print output

		remote_conn.send(root_pass)
		remote_conn.send('\n')
		time.sleep(2)
		output = remote_conn.recv(65535)
		print output

		remote_conn.send(root_pass)
		remote_conn.send('\n')
		time.sleep(2)
		output = remote_conn.recv(65535)
		print output

		remote_conn.close()
		client.close()
		time.sleep(5)
		print "Changing Root Password on %s Succeeded" %(ip)
	except:
		print "Changing Root Password on %s failed" %ip

###################    start    ####################

print "set_ifc_description is ", set_ifc_description 
print "change_ipmi_address is ", change_ipmi_address 
print "change_root_password is ", change_root_password 
print "oob_sw_ip is ", oob_sw_ip 
print "oob_sw_username is ", oob_sw_username 
print "oob_sw_password is ", oob_sw_password 
print "default_initial_ip is ", default_initial_ip 
print "default_initial_password is ", default_initial_password 
print "new_root_password is ", new_root_password 
print "IPMI subnetmask is ", subnetmask 
print "IPMI gateway is ", gateway 
print "##################################"
print ""

try:
	file = open(info_file, 'r')
except IOError as e:
	print e
	print "Please configure the parameter <info_file> with the correct info file path"
	quit()

file_lines = file.readlines()
file.close()

# Connect to the switch
switch = paramiko.SSHClient()
switch.set_missing_host_key_policy(paramiko.AutoAddPolicy())
switch.connect(oob_sw_ip, username=oob_sw_username, password=oob_sw_password, look_for_keys=False, allow_agent=False)

switch_remote_conn = switch.invoke_shell()
switch_remote_conn.send ('sys\n')

# shutdown all interfaces connected to rack servers
for line in file_lines:
#	print line
	ifc=line.split(',')[1].strip('\n')
	switch_remote_conn.send('interface GE ')
	switch_remote_conn.send(ifc)
	switch_remote_conn.send('\n')
	time.sleep(1)
	switch_remote_conn.send('shutdown\n')
	time.sleep(1)
	sw_output = switch_remote_conn.recv(65535)
	print sw_output

switch_remote_conn.send('commit\n')
time.sleep(5)

'''
1- open interface on switch one by one and add description to the interface
2- change IP address
3- Change root password
'''

interfaces=[]
for line in file_lines:
	ifc=line.split(',')[1].strip('\n')
	interfaces.append(ifc)
	ipmi_ip=line.split(',')[0].strip()
	print "configuring: " + ipmi_ip + " connected to interface " + ifc

# [1]
	if set_ifc_description is True:
		description=line.split(',')[2].strip('\n')
		
		switch_remote_conn.send('interface GE ')
		switch_remote_conn.send(ifc)
		switch_remote_conn.send('\n')
		time.sleep(1)
		
		switch_remote_conn.send('description ')
		switch_remote_conn.send(description)
		switch_remote_conn.send('\n')
		time.sleep(1)
	else:
		switch_remote_conn.send('interface GE ')
		switch_remote_conn.send(ifc)
		switch_remote_conn.send('\n')
		time.sleep(1)

	switch_remote_conn.send('undo shutdown \n')
	time.sleep(1)
	switch_remote_conn.send('commit \n')
	time.sleep(1)
	sw_output = switch_remote_conn.recv(65535)
	print sw_output

# [2]
	if change_ipmi_address is True:
		server = ping_host(default_initial_ip)
		if server is True:
			ipmi_change = change_ipmi_ip(ipmi_ip)
		else:
			ipmi_change = False
	else:
		ipmi_change = True

# [3]
	if change_root_password is True:
		if ipmi_change is True:
			change_password(ipmi_ip)
			
# Shutdown the interface after configuring the server
	switch_remote_conn.send('interface GE ')
	switch_remote_conn.send(ifc)
	switch_remote_conn.send('\n')
	time.sleep(1)
	switch_remote_conn.send('shutdown\n')
	time.sleep(1)
	switch_remote_conn.send('commit \n')
	time.sleep(2)
	sw_output = switch_remote_conn.recv(65535)
	print sw_output
		
# Open all interfaces after finishing configuration
for i in interfaces:
	switch_remote_conn.send('interface GE ')
	switch_remote_conn.send(i)
	switch_remote_conn.send('\n')
	time.sleep(1)
	switch_remote_conn.send('undo shutdown \n')
	time.sleep(1)

switch_remote_conn.send('commit \n')
sw_output = switch_remote_conn.recv(65535)
time.sleep(2)
print sw_output
switch_remote_conn.close()
###############################################
usr = raw_input('Would you like to change blades password?: (press "Enter" or "y" to continue or Any other key to abort)')

if re.search("^y",usr,flags=re.IGNORECASE) or re.search('^$',usr):
	print "Confiruring Blades Root Password !!!"
	time.sleep(1)
	root_pswd_blades.run()
else:
	print "Input value is %s" %usr
	print "Aborting"