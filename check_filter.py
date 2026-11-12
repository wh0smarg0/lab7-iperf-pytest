from client import client
from parser import parser

server_ip = "192.168.100.100"

results, error = client(server_ip)

if error:
	print("IPERF ERROR:", error)
else:
	intervals = parser(results)

	print(f"PARSED INTERVALS: {len(intervals)}")
	print("\n=== FILTERED RESULTS ===")

	filtered = [
		interval for interval in intervals
		if interval["transfer_mb"] > 2
		and interval["bitrate_mbps"] > 20
	]

	for interval in filtered:
		print(
			f"{interval['start']:.1f}-{interval['end']:.1f} sec | "
			f"Transfer: {interval['transfer_mb']:.2f} MB | "
			f"Bitrate: {interval['bitrate_mbps']:.2f} Mbit/s"
		)

	print(f"\nFILTERED INTERVALS: {len(filtered)}")
