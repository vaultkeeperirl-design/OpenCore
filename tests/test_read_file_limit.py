import os
import unittest
import tempfile
from opencore.tools.base import read_file, MAX_READ_SIZE

class TestReadFileLimit(unittest.TestCase):
    def setUp(self):
        # Use current working directory to avoid path traversal checks failing
        # We'll clean up manually
        self.large_file = "test_large.txt"
        self.small_file = "test_small.txt"

        # Create a file slightly larger than MAX_READ_SIZE
        # We don't need to make it huge, just 1 byte over limit is enough to trigger truncation logic check
        # But to be safe and fast, let's just make a file of size MAX_READ_SIZE + 100
        # However, to avoid writing 10MB to disk in test every time, we can mock MAX_READ_SIZE?
        # But MAX_READ_SIZE is a constant. We can't easily mock it without patching.
        # Let's write the actual 10MB file. It's fast enough on modern SSDs.

        # Create a file slightly larger than MAX_READ_SIZE (10MB + 100 bytes)
        with open(self.large_file, "w") as f:
            # Write 'A's to fill up to limit, then 'B's over limit
            # This ensures it's text content, not binary nulls which might be read weirdly
            chunk = "A" * (1024 * 1024) # 1MB chunk
            for _ in range(10):
                f.write(chunk)
            f.write("B" * 100)

        with open(self.small_file, "w") as f:
            f.write("Hello World")

    def tearDown(self):
        if os.path.exists(self.large_file):
            os.remove(self.large_file)
        if os.path.exists(self.small_file):
            os.remove(self.small_file)

    def test_read_small_file(self):
        content = read_file(self.small_file)
        self.assertEqual(content, "Hello World")

    def test_read_large_file_truncation(self):
        content = read_file(self.large_file)
        self.assertLess(len(content), MAX_READ_SIZE + 100)
        self.assertTrue(content.endswith("reached...]"))
        self.assertIn("File truncated", content)

if __name__ == "__main__":
    unittest.main()
