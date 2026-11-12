from client import client
from parser import parser

output, error = client("192.168.100.100")

if error:
    print("ERROR:", error)
else:
    results = parser(output)

    print("\n=== PARSED RESULTS ===")

    for interval in results:
        print(
            f"{interval['start']:.1f}-{interval['end']:.1f} sec | "
            f"Transfer: {interval['transfer_mb']:.2f} MB | "
            f"Bitrate: {interval['bitrate_mbps']:.2f} Mbit/s"
        )

    print(f"\nPARSED INTERVALS: {len(results)}")
