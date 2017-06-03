import re
import string
import dns
from dns import resolver # dnspython==1.16.0
import socket
import smtplib

VIABLE = string.ascii_letters + string.digits + "-" + "_"

def check(addressToVerify):
	match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify)	
	if match == None:
		return False

	try:
		records = dns.resolver.query("gmail.com", 'MX')
		mxRecord = records[0].exchange
		mxRecord = str(mxRecord)
	except:
		print('Failed')
		return False
	'''
	broke = re.split("[@.]+", addressToVerify)
        valid = True;
        for st in broke:
            valid ^= st in VIABLE
        return valid
       '''

	# Get local server hostname
	host = socket.gethostname()

	# SMTP lib setup (use debug level for full output)
	server = smtplib.SMTP()
	server.set_debuglevel(0)

	# SMTP Conversation
	server.connect(mxRecord)
	server.helo(host)
	server.mail('me@domain.com') # parameter is sender's address
	code, message = server.rcpt(str(addressToVerify))
	server.quit()

	# Assume 250 as Success
	if code == 250:
		return True
	else:
		return False

if __name__ == '__main__':

	emails = ["jamie.zimmerman4@gmail.com", '"jamie.zimmerman4@gmail.com']
	for email in emails:
		if check(email):
			print("email address: {} Final Success".format(email))
		else:
			print("email address: {} Final Failure".format(email))




