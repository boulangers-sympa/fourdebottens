"""Remove EXIF/GPS and other metadata from JPEG files, in place or to a new path.

Drops APP1..APP15 and COM segments (keeps APP0/JFIF so colours and density stay).
No dependencies. Usage: python3 strip_jpeg_metadata.py in.jpg [out.jpg]
"""
import sys


def strip(data: bytes) -> bytes:
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG")
    out = bytearray(b"\xff\xd8")
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            raise ValueError(f"bad marker at {i}")
        marker = data[i + 1]
        if marker == 0xDA:  # start of scan: the rest is image data
            out += data[i:]
            return bytes(out)
        length = int.from_bytes(data[i + 2:i + 4], "big")
        segment = data[i:i + 2 + length]
        if not (0xE1 <= marker <= 0xEF or marker == 0xFE):
            out += segment
        i += 2 + length
    return bytes(out)


if __name__ == "__main__":
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src
    with open(src, "rb") as f:
        cleaned = strip(f.read())
    with open(dst, "wb") as f:
        f.write(cleaned)
