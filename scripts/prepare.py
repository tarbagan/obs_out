"""Prepare a pinned OBS build tree and overlay the maintained DeckLink modules."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify_archive(archive: Path, expected: str) -> None:
    actual = hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f"OBS archive checksum mismatch: {actual}; expected {expected}")


def extract_checked(archive: Path, destination: Path) -> None:
    destination = destination.resolve()
    with zipfile.ZipFile(archive) as source:
        regular_entries = []
        for item in source.infolist():
            target = (destination / item.filename).resolve()
            if not target.is_relative_to(destination):
                raise ValueError(f"Unsafe archive path: {item.filename}")
            if (item.external_attr >> 16) & 0o170000 == 0o120000:
                # OBS includes macOS helper symlinks. Windows module builds do not
                # need them; never create or follow links from an archive.
                continue
            regular_entries.append(item)
        source.extractall(destination, members=regular_entries)


def prepare(root: Path = ROOT, archive: Path | None = None) -> Path:
    lock = json.loads((root / "upstream.lock.json").read_text(encoding="utf-8"))
    dependencies = root / ".deps"
    dependencies.mkdir(exist_ok=True)
    archive = archive or dependencies / "obs-source.zip"
    if not archive.exists():
        url = f"https://codeload.github.com/obsproject/obs-studio/zip/{lock['commit']}"
        partial = archive.with_suffix(".download")
        print(f"Downloading {url}", flush=True)
        with urllib.request.urlopen(url, timeout=60) as response, partial.open("wb") as target:
            shutil.copyfileobj(response, target)
        verify_archive(partial, lock["archive_sha256"])
        partial.replace(archive)
    verify_archive(archive, lock["archive_sha256"])
    tree = dependencies / f"obs-studio-{lock['commit']}"
    if not (tree / "CMakeLists.txt").exists():
        extract_checked(archive, dependencies)
    for module in ("decklink", "decklink-output-ui"):
        shutil.copytree(root / "plugins" / module, tree / "plugins" / module, dirs_exist_ok=True)
    # Only these modules are configured. No browser/websocket/capture submodules needed.
    (tree / "plugins" / "CMakeLists.txt").write_text(
        'cmake_minimum_required(VERSION 3.28...3.30)\n'
        '# libobs is built for import libraries only; do not make upstream warnings fatal.\n'
        'set_property(TARGET libobs PROPERTY COMPILE_WARNING_AS_ERROR OFF)\n'
        'add_subdirectory(decklink)\nadd_subdirectory(decklink-output-ui)\n', encoding="utf-8"
    )
    return tree


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="Use an already downloaded, checksum-verified archive")
    args = parser.parse_args()
    print(prepare(archive=args.archive))
