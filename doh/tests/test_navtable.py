import unittest

from test_data import *
from main import *

class NavigationParser(unittest.TestCase):
    def test_parse_navtable(self):
        topics = parse_discourse_navigation_table(simple_case)
        self.assertEqual(topics, simple_case_result)

        topics = parse_discourse_navigation_table(different_link_types)
        self.assertEqual(topics, different_link_types_result)

if __name__ == '__main__':
    unittest.main()