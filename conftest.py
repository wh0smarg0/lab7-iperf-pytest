import os
import socket
import subprocess
import time

import paramiko
import pytest

from parser import parser


SERVER_PORT = 5001
TASK_NAME = "LabIperfServer"


@pytest.fixture(scope="module")
def iperf_server():
	"""Start iperf server on Windows over SSH."""

	host = os.environ["IPERF_HOST"]
	username = os.environ["IPERF_SSH_USER"]
	password = os.environ["IPERF_SSH_PASSWORD"]

	ssh = paramiko.SSHClient()
	ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(paramiko.RejectPolicy())

	ssh.connect(
		hostname=host,
		username=username,
		password=password,
		timeout=10,
		look_for_keys=False,
		allow_agent=False,
	)

	try:
		# Check whether the port is already occupied.
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
			sock.settimeout(2)

			if sock.connect_ex((host, SERVER_PORT)) == 0:
				pytest.fail(
					f"Port {SERVER_PORT} is already occupied on {host}"
					"Server stop existing iperf server before testing"
				)

		# Start iperf on Windows through SSH.
		command = (
			f"schtasks /Run /TN {TASK_NAME}"
		)

		_, stdout, stderr = ssh.exec_command(command)

		output = stdout.read().decode(errors="replace").strip()
		error = stderr.read().decode(errors="replace").strip()
		exit_status = stdout.channel.recv_exit_status()

		if exit_status != 0:
			pytest.fail(
				f"Failed to start remote iperf server: "
				"{error or output}"
			)

		print(f"\n[SETUP] {output}")

		# Wait for the server to start listening.
		for _ in range(20):
			with socket.socket(
				socket.AF_INET, socket.SOCK_STREAM
			) as sock:
				sock.settimeout(1)

				if sock.connect_ex((host, SERVER_PORT)) == 0:
					print(
						f"[SETUP] iperf server ready "
						f"on {host}:{SERVER_PORT}"
					)
					break

			time.sleep(0.5)
		else:
			pytest.fail("Remote iperf server did not start")

		yield host

	finally:
		command = (
			'powershell -NoProfile -NonInteractive -Command '
			'"Get-Process iperf -ErrorAction SilentlyContinue | '
			'Stop-Process -Force"'
		)

		try:
			_, stdout, stderr = ssh.exec_command(command)
			exit_status = stdout.channel.recv_exit_status()

			if exit_status == 0:
				print("\n[TEARDOWN] Remote iperf server stopped")
			else:
				error = stderr.read().decode(errors="replace").strip()
				print(f"\n[TEARDOWN] Stop command failed: {error}")

		finally:
			ssh.close()

@pytest.fixture(scope="module")
def iperf_results(iperf_server):
	"""Run the iperf client and parse its output."""

	command = [
		"iperf",
		"-c", iperf_server,
		"-p", str(SERVER_PORT),
		"-i", "1",
		"-t", "10",
	]

	print("\n[CLIENT] running iperf client...")
	print(f"[CLIENT] command: {' '.join(command)}")

	result = subprocess.run(
		command,
		capture_output=True,
		text=True,
		timeout=25,
		check=False,
	)

	print("\n[CLIENT] iperf output: ")
	print(result.stdout)

	if result.returncode != 0:
		pytest.fail(
			f"iperf client failed:\n{result.stderr}"
		)

	intervals = parser(result.stdout)

	if not intervals:
		pytest.fail("No iperf intervals were parsed")

	print(f"[CLIENT] parsed {len(intervals)} intervals")

	for interval in intervals:
		print(
			f"[RESULT] {interval['start']:.1f}-"
			f"{interval['end']:.1f} sec | "
			f"Transfer: {interval['transfer_mb']:.2f} MBytes | "
			f"Bandwidth: {interval['bitrate_mbps']:.2f} Mbit/s"
		)

	return intervals
