#####################################
# Mohamed Gamal El-Naggar           #
# email: mgamal@eventumsolutions.com#
#####################################

import paramiko
import time
import re
from datetime import datetime

################################################################
username = 'eventum'
password = 'P@ssw0rd123'
ip_address = {'10.52.49.12':'ToR','10.52.49.90':'E9K'}

date = str(datetime.now()).split('.')[0].replace(':','-').replace(' ','_')
report_file = 'SFP-Power report_' + date + '.csv'

ToR_cmd = 'display interface transceiver brief | no-more \n'
ToR_th = -5.0
E9k_cmd = 'display interface transceiver verbose | no-more \n'
E9K_th = -5.0
###############################################################

def desc_report (remote_conn,report,device,ifc_name,txrx,power):
	remote_conn.send('display int desc %s \n' %(ifc_name))
	time.sleep(1)
	desc = remote_conn.recv(65535).split(ifc_name)[2].split('<')[0].strip()
	report.write(("%s,%s,%s_power,%s,%s\n")%(device,ifc_name,txrx,power,desc))

report = open (report_file, 'w+')
report.write("Node,Interface,sent/received,power,PHY  Protocol   description \n")

for dev in ip_address.keys():
	print ip_address[dev] + '---' + dev
	f_name = str(ip_address[dev]) + '-' + dev + '.txt'
	file = open (f_name, 'w+')
	# Connect to node
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(dev, username=username, password=password, look_for_keys=False, allow_agent=False)
	remote_conn = client.invoke_shell()
	time.sleep(1)
	if ip_address[dev] is 'ToR':
		cmd = ToR_cmd
	elif ip_address[dev] is 'E9K':
		cmd = E9k_cmd
	# run the display command
	remote_conn.send(cmd)
	time.sleep(10)
	# Retrieve the output
	output = remote_conn.recv(65535)
	# Write the output to file and save it
	file.write(output)
	file.close()
	# Open the file again but in read only mode
	f = open (f_name , 'r+')
	info = f.readlines()
	for line in info:
		# Skip un wanted lines
		if re.match('^$',line) or re.match('^  ',line) or re.match('^--',line) or re.match('40GE',line):
			continue
		# The output of ToR switches contains the word "transceiver diagnostic"
		if "transceiver diagnostic" in line: 					#ToR switches
			# Get the interface name
			ifc = line.split('transceiver')[0].strip()
			# Get the line index in the file
			ind = info.index(line)
			# Get received power value
			rcv_pwr = info[ind+5].split(":")[1].strip()
			# Check the value vs. the threshold
			if float(rcv_pwr) < ToR_th:
				# Get the interface PHY status, protocol status and description then write the output to the report
				desc_report(remote_conn,report,dev,ifc,'received',rcv_pwr)
			# Get the sent power value
			sent_pwr= info[ind+6].split(":")[1].strip()
			# Check the value vs. the threshold
			if float(sent_pwr) < ToR_th:
				# Get the interface PHY status, protocol status and description then write the output to the report
				desc_report(remote_conn,report,dev,ifc,'sent',sent_pwr)

		# The output of E9K switches contains the word "transceiver information"
		if "transceiver information:" in line: 					 #E9k switches
			ifc = line.split('transceiver')[0].strip()
			ind = info.index(line)
			rcv_pwr = info[ind+28].split(":")[1].strip()
			if float(rcv_pwr) < E9K_th:
				desc_report(remote_conn,report,dev,ifc,'received',rcv_pwr)
			sent_pwr= info[ind+31].split(":")[1].strip()
			if float(sent_pwr) < E9K_th:
				desc_report(remote_conn,report,dev,ifc,'sent',sent_pwr)
	# Close the connection
	remote_conn.close()
	f.close()
report.close()