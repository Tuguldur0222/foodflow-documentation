"""Generate intentionally synthetic JPEG and WAV upload fixtures."""

import math
from pathlib import Path
import struct
import wave

from PIL import Image


def main():
    destination = Path(__file__).parent
    image = Image.new("RGB", (32, 32))
    image.putdata([
        (240, 240, 240) if (x // 8 + y // 8) % 2 == 0 else (30, 30, 30)
        for y in range(32) for x in range(32)
    ])
    image.save(destination / "einstein.jpg", format="JPEG", quality=90)
    with wave.open(str(destination / "einstein_bark.wav"), "wb") as audio:
        audio.setparams((1, 2, 8000, 800, "NONE", "not compressed"))
        audio.writeframes(b"".join(struct.pack("<h", int(3000 * math.sin(2 * math.pi * 440 * index / 8000))) for index in range(800)))


if __name__ == "__main__":
    main()
