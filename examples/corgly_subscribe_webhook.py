"""UE-5: register a local pet.activity callback URL with the Corg.ly mock.

The mock returns an acknowledgement and does not send callbacks or verify the
receiver. The sample URL is local training data, not a deployed webhook service.
"""

import argparse
import json
from urllib.request import Request, urlopen


def run(base_url="http://127.0.0.1:8765"):
    subscription = {"url": base_url.rstrip("/") + "/webhook-receiver", "events": ["pet.activity"]}
    request = Request(
        base_url.rstrip("/") + "/v1/webhooks/subscribe", data=json.dumps(subscription).encode("utf-8"),
        headers={"Authorization": "Bearer demo-corgly-token", "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        result = json.load(response)
        if response.status != 201:
            raise RuntimeError(f"Expected HTTP 201, received {response.status}")
        print(response.status, json.dumps(result, ensure_ascii=False))
        return response.status, result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    run(parser.parse_args().base_url)
