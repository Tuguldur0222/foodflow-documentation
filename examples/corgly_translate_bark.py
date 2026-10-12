"""UE-5: send a synthetic WAV to a local mock and read a fixed translation.

The WAV is a generated tone, not a real bark. This endpoint demonstrates the
request format and does not implement animal sound recognition or translation.
"""

import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen


def run(base_url="http://127.0.0.1:8765"):
    audio_bytes = (Path(__file__).parent / "data/einstein_bark.wav").read_bytes()
    request = Request(
        base_url.rstrip("/") + "/v1/audio/translate-bark", data=audio_bytes,
        headers={"Authorization": "Bearer demo-corgly-token", "Content-Type": "audio/wav",
                 "X-Pet-Id": "corgi_98231", "X-Target-Language": "en"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        result = json.load(response)
        if response.status != 200:
            raise RuntimeError(f"Expected HTTP 200, received {response.status}")
        print(response.status, json.dumps(result, ensure_ascii=False))
        return response.status, result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    run(parser.parse_args().base_url)
