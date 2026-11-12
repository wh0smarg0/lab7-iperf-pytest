import subprocess

server_ip = "192.168.100.100"

def client(server_ip):
	command = [
		"iperf",
		"-c", server_ip,
		"-i", "1",
		"-t", "10"
	]

	try:
		process = subprocess.Popen(
			command,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True
		)

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			return stdout, stderr or f"IPERF EXITED WITH CODE {process.returncode}"

		return stdout, stderr

	except OSError as error:
		return "", str(error)

if __name__ == "__main__":
	result, error = client(server_ip)

	if error:
		print("ERROR:", error)
	else:
		print("IPERF EXECUTED SUCCESSFULLY!")
		print(result)
