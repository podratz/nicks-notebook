import argparse
import datetime
import unittest

from src import note


def setup_date_args(yesterday=False, today=False, tomorrow=False):
    parser = argparse.ArgumentParser()
    parser.add_argument("--yesterday", default=yesterday)
    parser.add_argument("--today", default=today)
    parser.add_argument("--tomorrow", default=tomorrow)
    return parser.parse_args()


class TestGenerateDateString(unittest.TestCase):
    def testWithSampleData(self):
        date = datetime.datetime.strptime("24052010", "%d%m%Y").date()
        format_str = "YYYY-MM-DD"
        dateString = note.generateDateString(format_str, date)
        self.assertEqual(dateString, "2010-05-24")


class TestNoteCommand(unittest.TestCase):
    def testComposeFilenameWithName(self):
        name = "pythagoras"
        filename = note.compose_filename([name])
        self.assertEqual(filename, "pythagoras.md")

    def testComposeFilenameWithDatePrefix(self):
        date_prefix = "2023-05-22"
        filename = note.compose_filename([date_prefix])
        self.assertEqual(filename, "2023-05-22.md")

    def testComposeFilenameWithDatePrefixAndName(self):
        date_prefix = "2023-05-22"
        name = "todo"
        filename = note.compose_filename([date_prefix, name])
        self.assertEqual(filename, "2023-05-22_todo.md")

    def testComposeFilenameWithoutFilenameArguments(self):
        self.assertRaises(ValueError, note.compose_filename, [])

    def test_extract_date_offset_for_yesterday(self):
        args = setup_date_args(yesterday=True)
        date_offset = note.extract_date_offset(args)
        self.assertEqual(date_offset, -1)

    def test_extract_date_offset_for_today(self):
        args = setup_date_args(today=True)
        date_offset = note.extract_date_offset(args)
        self.assertEqual(date_offset, 0)

    def test_extract_date_offset_for_tomorrow(self):
        args = setup_date_args(tomorrow=True)
        date_offset = note.extract_date_offset(args)
        self.assertEqual(date_offset, +1)

    def test_extract_date_offset_with_no_args(self):
        args = setup_date_args()
        date_offset = note.extract_date_offset(args)
        self.assertEqual(date_offset, None)


if __name__ == "__main__":
    unittest.main()
