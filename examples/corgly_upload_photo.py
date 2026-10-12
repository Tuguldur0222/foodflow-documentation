"""UE-5: upload a synthetic JPEG for corgi_98231 to the local Corg.ly mock.

The bundled image is a generated checkerboard, not a photograph of a pet.
Start the mock first; this example requires only the Python standard library.
"""

import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen


def run(base_url="http://127.0.0.1:8765"):
    photo_bytes = (Path(__file__).parent / "data/einstein.jpg").read_bytes()
    boundary = "CorglyEinsteinPhotoBoundary"
    multipart_body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="pet_id"\r\n\r\ncorgi_98231\r\n'
        f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="einstein.jpg"\r\n'
        'Content-Type: image/jpeg\r\n\r\n'
    ).encode() + photo_bytes + f"\r\n--{boundary}--\r\n".encode()
    request = Request(
        base_url.rstrip("/") + "/v1/pets/upload-photo", data=multipart_body,
        headers={"Authorization": "Bearer demo-corgly-token", "Content-Type": f"multipart/form-data; boundary={boundary}"},
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
