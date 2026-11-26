import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "prepare.py"
spec = importlib.util.spec_from_file_location("prepare", SCRIPT)
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class SourcePreparationTests(unittest.TestCase):
    def test_rejects_corrupt_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "source.zip"
            archive.write_bytes(b"corrupt")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                prepare.verify_archive(archive, "0" * 64)

    def test_rejects_path_traversal_before_extracting(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "source.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("safe.txt", "safe")
                z.writestr("../escaped.txt", "bad")
            destination = Path(tmp) / "extracted"
            with self.assertRaisesRegex(ValueError, "Unsafe archive path"):
                prepare.extract_checked(archive, destination)
            self.assertFalse((destination / "safe.txt").exists())
            self.assertFalse((Path(tmp) / "escaped.txt").exists())

    def test_rejects_archive_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "source.zip"
            with zipfile.ZipFile(archive, "w") as z:
                item = zipfile.ZipInfo("link")
                item.create_system = 3
                item.external_attr = 0o120777 << 16
                z.writestr(item, "../outside")
            with self.assertRaisesRegex(ValueError, "symlink"):
                prepare.extract_checked(archive, Path(tmp) / "extracted")

    def test_overlay_is_repeatable_and_includes_both_modules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "source.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("obs-studio-test/CMakeLists.txt", "project(upstream)")
                z.writestr("obs-studio-test/plugins/CMakeLists.txt", "original plugins")
            lock = {"commit": "test", "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}
            (root / "upstream.lock.json").write_text(json.dumps(lock))
            for module in ("decklink", "decklink-output-ui"):
                path = root / "plugins" / module
                path.mkdir(parents=True)
                (path / "CMakeLists.txt").write_text(module)
            tree = prepare.prepare(root, archive)
            self.assertEqual((tree / "plugins/decklink/CMakeLists.txt").read_text(), "decklink")
            self.assertIn("add_subdirectory(decklink-output-ui)", (tree / "plugins/CMakeLists.txt").read_text())
            (root / "plugins/decklink/CMakeLists.txt").write_text("updated")
            self.assertEqual(prepare.prepare(root, archive), tree)
            self.assertEqual((tree / "plugins/decklink/CMakeLists.txt").read_text(), "updated")


if __name__ == "__main__":
    unittest.main()
