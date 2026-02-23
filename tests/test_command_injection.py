import unittest
import os
from opencore.tools.base import execute_command

class TestCommandInjection(unittest.TestCase):
    def test_command_injection(self):
        """
        Tests if command injection via shell operators is possible.
        If shell=True (vulnerable), this will create a file.
        If shell=False (secure), this will fail or print the redirect as text.
        """
        filename = "injected_file.txt"

        # Ensure cleanup
        if os.path.exists(filename):
            os.remove(filename)

        try:
            # Vulnerable command: echo test > injected_file.txt
            # If vulnerable, file is created.
            # If secure, 'echo' prints "test > injected_file.txt" to stdout and file is NOT created.
            command = f"echo test > {filename}"
            result = execute_command(command)

            # Check if file exists
            if os.path.exists(filename):
                self.fail("Security Failure: File created via shell injection (Vulnerability exists)")
            else:
                # Expected behavior: File is NOT created
                # Check output contains the literal redirect characters (because echo printed them)
                self.assertIn(">", result)
                self.assertIn(filename, result)

        finally:
            if os.path.exists(filename):
                os.remove(filename)

    def test_chained_command(self):
        """
        Tests chained commands like 'ls && touch hacked.txt'
        """
        filename = "hacked.txt"
        if os.path.exists(filename):
            os.remove(filename)

        try:
            # Command: echo safe && touch hacked.txt
            # With shell=False, 'echo' receives "safe", "&&", "touch", "hacked.txt" as args
            # It will print them. 'touch' will NOT run.
            command = f"echo safe && touch {filename}"
            result = execute_command(command)

            if os.path.exists(filename):
                self.fail("Security Failure: Chained command executed (Vulnerability exists)")
            else:
                self.assertIn("&&", result)
                self.assertIn("touch", result)

        finally:
             if os.path.exists(filename):
                os.remove(filename)

    def test_valid_command(self):
        """Tests that valid commands still work."""
        result = execute_command("echo hello")
        self.assertIn("hello", result)
