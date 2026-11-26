"""Front-page image entry for the news-image-20261126 bounty.

The entry is a one-page newspaper front page for Thursday
26 November 2026, built from the news reported that day. Its lead
stories are the first anniversary of the Wang Fuk Court fire in
Hong Kong, leaked figures on Russian war dead, a graft probe into
Shanghai party chief Chen Jining, Kilmar Abrego Garcia arriving
in Spain, a new US tariff plan, and the World Chess Championship,
with a ticker carrying six further items from the day.

The finished picture ships with this repository as entry.png.
The hero artwork (Tai Po's towers at dusk, candles and flowers
laid in memory) was made in the builder session and holds no
words of its own; every headline, the dateline and the captions
were drawn on top of it with PIL and DejaVu fonts, so the text
stays sharp. All this script does is check that shipped file
and place a copy of it where the grader looks for it.

It needs nothing but the standard library, talks to no network,
takes no input, and always writes the same bytes: the copy is
verified against the shipped file's SHA-256 before it reports
success.
"""

import hashlib
import os
import shutil
import struct
from pathlib import Path

SHIPPED_NAME = "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
LIMIT_BYTES = 1_048_576
LIMIT_SIDE = 1024


def sha256_of(path: Path) -> str:
    """Return the hex SHA-256 digest of a file's bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_png(path: Path) -> tuple[int, int, int]:
    """Check path is a PNG inside the competition limits.

    Returns the (width, height, size in bytes) triple. Anything
    off -- wrong magic, a missing IHDR chunk, over the 1 MiB cap,
    or a side longer than 1024 pixels -- raises ValueError.
    """
    blob = path.read_bytes()
    if blob[:8] != PNG_MAGIC:
        raise ValueError(f"{path} does not start with the PNG magic")
    if blob[12:16] != b"IHDR":
        raise ValueError(f"{path} has no IHDR chunk where one belongs")
    size = len(blob)
    if size > LIMIT_BYTES:
        raise ValueError(
            f"{path} is {size} bytes, over the {LIMIT_BYTES} byte cap"
        )
    width, height = struct.unpack(">II", blob[16:24])
    if width > LIMIT_SIDE or height > LIMIT_SIDE:
        raise ValueError(
            f"{path} is {width}x{height}, over the {LIMIT_SIDE}x{LIMIT_SIDE} cap"
        )
    return width, height, size


def main() -> None:
    """Validate the shipped front page and copy it to /output."""
    here = Path(__file__).resolve().parent
    shipped = here / SHIPPED_NAME
    if not shipped.is_file():
        raise FileNotFoundError(f"no shipped image at {shipped}")
    width, height, size = inspect_png(shipped)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    written = out_dir / SHIPPED_NAME
    shutil.copyfile(shipped, written)
    before = sha256_of(shipped)
    after = sha256_of(written)
    if before != after:
        raise ValueError(f"copy to {written} does not match {shipped}")
    print(
        f"wrote {written} ({width}x{height}, {size} bytes, "
        f"sha256 {before})"
    )


if __name__ == "__main__":
    main()
