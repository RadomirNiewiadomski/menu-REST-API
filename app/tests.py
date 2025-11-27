"""
This module contains dummy test.
"""

from django.test import SimpleTestCase


class CalcTests(SimpleTestCase):
    """Test the calc module."""

    def test_add_numbers(self):
        """Test adding numbers together."""
        res = 5 + 6
        self.assertEqual(res, 11)
