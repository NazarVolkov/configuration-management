"""Проверки загрузки VFS и операций только в памяти."""

import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vfs import VirtualFS


class VfsTests(unittest.TestCase):
    def test_files_and_directories(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "docs").mkdir()
            (base / "docs" / "hello.txt").write_text("hello")
            vfs = VirtualFS(base)
            self.assertEqual(vfs.contents("/"), ["docs"])
            self.assertEqual(vfs.contents("/docs"), ["hello.txt"])
            self.assertEqual(vfs.files["/docs/hello.txt"], b"hello")

    def test_changes_only_in_memory(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            original = (base / "original.txt")
            original.write_text("data")
            vfs = VirtualFS(base)
            vfs.mkdir("/virtual")
            vfs.touch("/virtual/file.txt")
            vfs.touch("/original.txt")
            self.assertIn("/virtual/file.txt", vfs.files)
            self.assertFalse((base / "virtual").exists())
            self.assertEqual(original.read_text(), "data")

    def test_missing_directory(self):
        with self.assertRaises(FileNotFoundError):
            VirtualFS("/this-vfs-path-does-not-exist-1234")

    def test_paths_check_intermediate_directories(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "file.txt").write_text("data")
            (base / "docs").mkdir()
            vfs = VirtualFS(base)
            self.assertEqual(vfs.resolve("/docs", "../docs/."), "/docs")
            self.assertEqual(vfs.resolve("/", "//docs"), "/docs")
            self.assertEqual(vfs.resolve("/", "../../"), "/")
            for path in ("file.txt/..", "file.txt/", "missing/.."):
                with self.subTest(path=path):
                    with self.assertRaises(NotADirectoryError):
                        vfs.resolve("/", path)


if __name__ == "__main__":
    unittest.main()
