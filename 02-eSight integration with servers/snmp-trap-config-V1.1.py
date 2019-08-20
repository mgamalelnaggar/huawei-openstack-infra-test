import paramiko
import time

#######################
esightip='10.55.49.133'
ip_file='ibmc.txt'
username="root"
password="Orange@2019"
director_host_ip= '10.55.49.6'
#######################

file = open(ip_file, 'r')
ip_address = file.readlines()


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


for ip in ip_address:
	ip = ip.strip('\n')
	print ip
	# client = paramiko.SSHClient()
	# client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(ip, username=username, password=password, look_for_keys=False, allow_agent=False)
	remote_conn = client.invoke_shell()
	
	time.sleep(5)

# Configure SNMP trap parameters

# Enable SNMP trap
	remote_conn.send('ipmcset -t trap -d state -v 1 enabled')
	remote_conn.send('\n')
	time.sleep(2)
	output = remote_conn.recv(65535)
	print output

# Config Trap version
	remote_conn.send('ipmcset -t trap -d version -v V3')
	remote_conn.send('\n')
	time.sleep(2)
	output = remote_conn.recv(65535)
	print output

# Config severity
	remote_conn.send('ipmcset -t trap -d severity -v all')
	remote_conn.send('\n')
	time.sleep(2)
	output = remote_conn.recv(65535)
	print output

# Choose user of the Traps
	# remote_conn.send('ipmcset -t trap -d user -v eSightMgmt')
	remote_conn.send('ipmcset -t trap -d user -v ')
	remote_conn.send(username)
	remote_conn.send('\n')
	time.sleep(2)
	output = remote_conn.recv(65535)
	print output

# Trap mode
	remote_conn.send('ipmcset -t trap -d mode -v 1')
	remote_conn.send('\n')
	time.sleep(4)
	output = remote_conn.recv(65535)
	print output

# Config eSight IP address
	remote_conn.send('ipmcset -t trap -d address -v 1 ')
	remote_conn.send(esightip)
	remote_conn.send('\n')
	remote_conn.send('\n')
	time.sleep(2)
	
# Enable ntp
	remote_conn.send('ipmcset -t ntp -d status -v enabled')
	remote_conn.send('\n')
	time.sleep(4)
	output = remote_conn.recv(65535)
	print output
	
# Add primary NTP server
	remote_conn.send('ipmcset -t ntp -d preferredserver -v ')
	remote_conn.send(director_host_ip)
	remote_conn.send('\n')
	time.sleep(4)
	output = remote_conn.recv(65535)
	print output
	
# Add Alternate NTP server
	remote_conn.send('ipmcset -t ntp -d alternativeserver -v 10.7.107.101')
	remote_conn.send('\n')
	time.sleep(4)
	output = remote_conn.recv(65535)
	print output

# Set Time Zone
	remote_conn.send('ipmcset -d timezone -v +2:00')
	remote_conn.send('\n')
	time.sleep(4)
	output = remote_conn.recv(65535)
	print output
	
	remote_conn.close()
