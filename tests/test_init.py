"""个人文件初始化只创建缺失文件，不依赖 Typst、字体或用户内容。"""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("content.toml", "content.en.toml")


class InitializationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="resume-init-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        (self.root / "resume").mkdir()
        shutil.copy2(ROOT / "Makefile", self.root / "Makefile")
        shutil.copy2(ROOT / "scripts/init_personal.py", self.root / "scripts/init_personal.py")
        self.samples = {}
        for name in NAMES:
            data = (ROOT / "tests/fixtures" / name).read_bytes()
            self.samples[name] = data
            (self.root / "resume" / name).write_bytes(data)
        self.private = self.root / "resume/private"

    def invoke(self):
        return subprocess.run([sys.executable, "scripts/init_personal.py"], cwd=self.root,
                              text=True, capture_output=True)

    def assert_public_samples_unchanged(self):
        for name, expected in self.samples.items():
            self.assertEqual((self.root / "resume" / name).read_bytes(), expected)

    def test_make_init_creates_both_files_without_build_tools(self):
        result = subprocess.run(["make", "init", "PYTHON=" + sys.executable,
                                 "TYPST=not-installed-fixture", "TINYMIST=not-installed-fixture"],
                                cwd=self.root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name, expected in self.samples.items():
            self.assertEqual((self.private / name).read_bytes(), expected)
            self.assertIn("已创建：resume/private/" + name, result.stdout)
        self.assert_public_samples_unchanged()
        self.assertFalse((self.root / "output").exists())
        self.assertFalse((self.root / "docs").exists())

    def test_repeated_initialization_preserves_edited_bytes_and_timestamps(self):
        self.private.mkdir()
        # 合成字节刻意不是 TOML：初始化不应读取、改写或校验已有个人内容。
        edited = b"PRIVATE_EDITED_FIXTURE\r\n\xff"
        timestamps = {}
        for name in NAMES:
            path = self.private / name
            path.write_bytes(edited + name.encode())
            os.utime(path, ns=(1_000_000_000, 1_000_000_000))
            timestamps[name] = path.stat().st_mtime_ns
        for _ in range(2):
            result = self.invoke()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for name in NAMES:
                path = self.private / name
                self.assertEqual(path.read_bytes(), edited + name.encode())
                self.assertEqual(path.stat().st_mtime_ns, timestamps[name])
                self.assertIn("跳过已有文件：resume/private/" + name, result.stdout)
        self.assert_public_samples_unchanged()

    def test_only_missing_language_is_created(self):
        self.private.mkdir()
        for existing in NAMES:
            with self.subTest(existing=existing):
                for path in self.private.iterdir():
                    path.unlink()
                (self.private / existing).write_bytes(b"KEEP_PRIVATE_FIXTURE")
                result = self.invoke()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                for name in NAMES:
                    expected = b"KEEP_PRIVATE_FIXTURE" if name == existing else self.samples[name]
                    self.assertEqual((self.private / name).read_bytes(), expected)
        self.assert_public_samples_unchanged()

    def test_concurrent_initialization_never_truncates_files(self):
        processes = [subprocess.Popen([sys.executable, "scripts/init_personal.py"], cwd=self.root,
                                      text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                     for _ in range(4)]
        for process in processes:
            stdout, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, stdout + stderr)
        for name in NAMES:
            self.assertEqual((self.private / name).read_bytes(), self.samples[name])
        self.assert_public_samples_unchanged()

    def test_existing_symlinks_are_not_followed_or_replaced(self):
        self.private.mkdir()
        target = self.root / "existing-synthetic-content.toml"
        target.write_bytes(b"KEEP_LINK_TARGET")
        missing = self.root / "missing-synthetic-content.toml"
        try:
            (self.private / NAMES[0]).symlink_to(target)
            (self.private / NAMES[1]).symlink_to(missing)
        except (OSError, NotImplementedError):
            self.skipTest("当前平台不支持创建测试符号链接")
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(target.read_bytes(), b"KEEP_LINK_TARGET")
        self.assertFalse(missing.exists())
        for name in NAMES:
            self.assertTrue((self.private / name).is_symlink())

    def test_missing_source_fails_without_creating_an_empty_personal_file(self):
        (self.root / "resume" / NAMES[0]).unlink()
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("初始化失败", result.stderr)
        self.assertFalse((self.private / NAMES[0]).exists())

    def test_directory_collision_fails_without_modifying_it(self):
        destination = self.private / NAMES[0]
        destination.mkdir(parents=True)
        marker = destination / "keep.txt"
        marker.write_bytes(b"KEEP_DIRECTORY")
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("个人文件路径已被目录占用", result.stderr)
        self.assertEqual(marker.read_bytes(), b"KEEP_DIRECTORY")


if __name__ == "__main__":
    unittest.main(verbosity=2)
