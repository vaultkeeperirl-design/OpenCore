import unittest
from fastapi.testclient import TestClient
from opencore.interface.api import app
import os

class TestStaticServing(unittest.TestCase):
    def test_index_serving(self):
        client = TestClient(app)
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        # Check if it is the next.js index file (usually contains _next)
        self.assertIn("_next", response.text)

    def test_version(self):
        from opencore import __version__
        self.assertEqual(__version__, "2.0.3")

if __name__ == "__main__":
    unittest.main()
