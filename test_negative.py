def test_bitate_negative(iperf_results):
	required_bitrate = 100000

	for interval in iperf_results:
		assert interval["bitrate_mbps"] > required_bitrate, (
			f"FAILED at {interval['start']:.1f} sec: "
			f"actual={interval['bitrate_mbps']:.2f} Mbit/s, "
			f"required>{required_bitrate} Mbits/s"
		)
