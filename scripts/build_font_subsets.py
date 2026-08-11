"""Dev-time only: download JetBrains Mono and regenerate the embedded font
subsets from it. Not run by the nightly workflow — the workflow just reads
the committed .woff2 subsets, so it never needs fonttools installed, and the
~270KB source TTFs never get committed to a repo that's meant to stay light.

Re-run this only if the character set the graphics use changes (new symbol,
new language label, etc).

    pip install fonttools brotli
    python scripts/build_font_subsets.py
"""
from __future__ import annotations

import subprocess
import sys
import urllib.request
from pathlib import Path

FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
SOURCE_RELEASE = "https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf"

# Every character the stats graphics draw: latin letters (language names,
# labels), digits, and the punctuation used in dates/percentages/bars.
CHARSET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    " .,:%-+#@_/()★"
)

SOURCES = {
    "JetBrainsMono-Regular.ttf": "stats-regular.woff2",
    "JetBrainsMono-Bold.ttf": "stats-bold.woff2",
}


def _download(src_name: str, dest: Path) -> None:
    url = f"{SOURCE_RELEASE}/{src_name}"
    print(f"downloading {url}")
    with urllib.request.urlopen(url, timeout=30) as response:
        dest.write_bytes(response.read())


def main() -> int:
    FONTS_DIR.mkdir(parents=True, exist_ok=True)

    for src_name, out_name in SOURCES.items():
        src = FONTS_DIR / f"_src_{src_name}"
        if not src.is_file():
            _download(src_name, src)

        out = FONTS_DIR / out_name
        subprocess.run(
            [
                sys.executable, "-m", "fontTools.subset", str(src),
                f"--text={CHARSET}",
                "--flavor=woff2",
                "--layout-features=",
                "--no-hinting",
                f"--output-file={out}",
            ],
            check=True,
        )
        print(f"wrote {out} ({out.stat().st_size} bytes)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
