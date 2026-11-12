import os
import paramiko

host = os.environ["IPERF_HOST"]
username = os.environ["IPERF_SSH_USER"]
password = os.environ["IPERF_SSH_PASSWORD"]

ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.RejectPolicy())

try:
	ssh.connect(
		hostname=host,
		username=username,
		password=password,
		timeout=10,
		look_for_keys=False,
		allow_agent=False,
	)

	stdin, stdout, stderr = ssh.exec_command("whoami")

	print("SSH connection successful!")
	print("Remote user:", stdout.read().decode().strip())

	error = stderr.read().decode().strip()
	if error:
		print("STDERR:", error)

finally:
	ssh.close()
