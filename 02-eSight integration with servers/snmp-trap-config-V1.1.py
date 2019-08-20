import paramiko
import time


# ip_address=['10.51.92.3','10.51.92.4','10.51.92.5','10.51.92.50','10.51.92.51','10.51.92.52','10.51.92.53','10.51.92.54','10.51.92.6','10.51.92.7','10.51.92.8','10.51.92.9','10.51.92.10','10.51.92.11','10.51.92.14','10.51.92.15','10.51.92.16','10.51.92.17','10.51.92.18','10.51.92.25','10.51.92.26','10.51.92.27','10.51.92.28','10.51.92.29','10.51.92.30','10.51.92.33','10.51.92.34','10.51.92.35','10.51.92.70','10.51.92.71','10.51.92.72','10.51.92.73']

#ip_address=['10.51.92.63','10.51.92.64','10.51.92.65','10.51.92.66','10.51.92.67','10.51.92.89','10.51.92.90','10.51.92.91','10.51.92.36','10.51.92.37','10.51.92.68','10.51.92.69','10.51.92.76','10.51.92.77','10.51.92.78','10.51.92.79']

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

# Add new User "eSightMgmt"	
'''
	remote_conn.send('ipmcset -d adduser -v eSightMgmt')
	remote_conn.send('\n')
	time.sleep(2)
	output = remote_conn.recv(65535)
	print output
'''
# Add the Password
'''
	remote_conn.send('Changeme_123')
	remote_conn.send('\n')
	time.sleep(2)
	output = remote_conn.recv(65535)
	print output
	
	remote_conn.send('Changeme_123')
	remote_conn.send('\n')
	time.sleep(2)
	output = remote_conn.recv(65535)
	print output
	
	remote_conn.send('Changeme_123')
	remote_conn.send('\n')
	time.sleep(2)
	output = remote_conn.recv(65535)
	print output
	time.sleep(1)
'''
# Adjust user priviledge
'''
	remote_conn.send('ipmcset -d privilege -v eSightMgmt 4')
	remote_conn.send('\n')
	time.sleep(1)
	
	remote_conn.send('Changeme_123')
	remote_conn.send('\n')
	time.sleep(2)
	output = remote_conn.recv(65535)
	print output
'''
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
