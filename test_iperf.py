import pytest

def test_transfer(iperf_results):
	for interval in iperf_results:
		assert interval["transfer_mb"] > 2, (
			f"Transfer too low at {interval['start']} sec: "
			f"{interval['transfer_mb']:.2f} Mb"
		)

def test_bitrate(iperf_results):
	for interval in iperf_results:
		assert interval["bitrate_mbps"] > 20, (
			f"Bitrate too low at {interval['start']} sec: "
			f"{interval['bitrate_mbps']:.2f} Mbits/sec"
		)

@pytest.mark.parametrize(
	"threshold, expected",
	[
		(20, True),
		(25, True),
		(100000, False),
	]
)

def test_bitrate_threshold(iperf_results, threshold, expected):
	actual = all(
		interval["bitrate_mbps"] > threshold
		for interval in iperf_results
	)

	assert actual == expected

def test_bitrate_negative(iperf_results):
	threshold = 100

	for interval in iperf_results:
		assert interval["bitrate_mbps"] > threshold, (
			f"Bandwidth too low: "
			f"{interval['bitrate_mbps']:.2f} Mbit/s "
			f"(required > {threshold} Mbit/s)"
		)
