import paramiko
import time


def run():
################################################
# CH121 V3
	# default_initial_password='Huawei12#$'
	# default_username = 'root'
	
# CH121 V5
	default_initial_password='Admin@9000'
	default_username = 'Administrator'

	new_root_password='Orange@2019'

	# file contains IPMI IPs of blade servers
	bld_ip_file = "02-bld_ip.txt"
################################################
	file = open(bld_ip_file, 'r')
	file_lines = file.readlines()
	file.close()

	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	for line in file_lines:
		ip=line.strip('\n')
		print "configuring: " + ip + "\n ######################"
		client.connect(ip, username=default_username, password=default_initial_password, look_for_keys=False, allow_agent=False)
		bld_remote_conn = client.invoke_shell()

		bld_remote_conn.send('ipmcset -d password -v ')
		bld_remote_conn.send(default_username)
		bld_remote_conn.send('\n')
		time.sleep(5)
		output = bld_remote_conn.recv(65535)
		print output

		bld_remote_conn.send(default_initial_password)
		bld_remote_conn.send('\n')
		time.sleep(2)
		output = bld_remote_conn.recv(65535)
		print output

		bld_remote_conn.send(new_root_password)
		bld_remote_conn.send('\n')
		time.sleep(2)
		output = bld_remote_conn.recv(65535)
		print output

		bld_remote_conn.send(new_root_password)
		bld_remote_conn.send('\n')
		time.sleep(2)
		output = bld_remote_conn.recv(65535)
		print output
	#remote_conn.close()