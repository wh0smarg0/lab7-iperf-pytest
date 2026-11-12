import re


def parser(output):
    pattern = re.compile(
        r"\[\s*\d+\]\s+"
        r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s+sec\s+"
        r"(\d+(?:\.\d+)?)\s+([KMG]?Bytes)\s+"
        r"(\d+(?:\.\d+)?)\s+([KMG]?bits/sec)",
        re.IGNORECASE
    )

    results = []

    transfer_factors = {
        "bytes": 1 / (1024 * 1024),
        "kbytes": 1 / 1024,
        "mbytes": 1,
        "gbytes": 1024,
    }

    bitrate_factors = {
        "kbits/sec": 0.001,
        "mbits/sec": 1,
        "gbits/sec": 1000,
    }

    for line in output.splitlines():
        match = pattern.search(line)

        if match is None:
            continue

        start, end, transfer, transfer_unit, bitrate, bitrate_unit = match.groups()

        duration = float(end) - float(start)

        # Відкидаємо підсумковий рядок
        if duration > 1.5:
            continue

        results.append({
            "start": float(start),
            "end": float(end),
            "transfer_mb": float(transfer) * transfer_factors[transfer_unit.lower()],
            "bitrate_mbps": float(bitrate) * bitrate_factors[bitrate_unit.lower()],
        })

    return results
