import importlib.util
import struct
import unittest
import zlib
from pathlib import Path


class BootPriorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).parents[1] / "tools/package_firmware.py"
        spec = importlib.util.spec_from_file_location("package_firmware", path)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def image(self):
        body = b"Synthetic firmware body" * 8
        header = struct.pack(
            "<IIQIII",
            0x96F3B83D,
            28,
            0x8000000012345678,
            512,
            len(body),
            zlib.crc32(body),
        )
        return header + b"\xff" * (512 - len(header)) + body

    def test_changes_only_priority_preserving_valid_payload(self):
        original = self.image()
        new_priority = 0x0104260401234567
        result, old_priority = self.module.set_boot_priority(original, new_priority)
        self.assertEqual(old_priority, 0x8000000012345678)
        self.assertEqual(result[:8], original[:8])
        self.assertEqual(result[16:], original[16:])
        self.assertEqual(struct.unpack_from("<Q", result, 8)[0], new_priority)

    def test_rejects_corrupt_body(self):
        original = bytearray(self.image())
        original[-1] ^= 1
        with self.assertRaises(ValueError):
            self.module.set_boot_priority(bytes(original), 1)

    def test_rejects_invalid_header(self):
        with self.assertRaises(ValueError):
            self.module.set_boot_priority(b"invalid", 1)


if __name__ == "__main__":
    unittest.main()
