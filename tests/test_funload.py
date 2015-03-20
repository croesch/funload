#!/usr/bin/env python3

import xml.etree.ElementTree as ElemT
import unittest
import os
import datetime

import funload


def get_item(testfile):
    file = open(os.path.expanduser("test_funload_files/" + testfile), 'r')
    return ElemT.parse(file).getroot().find('channel').find('item')


class TestSequenceFunctions(unittest.TestCase):
    def test_multiple_youtube_links(self):
        item = get_item("test_multiple_youtube_links")
        date = datetime.datetime(2007, 12, 5)

        urls = funload.item_node_parse(item, date)
        self.assertEqual(urls, ["https://www.youtube.com/embed/Vx-1LQu6mAE?rel=0&amp;showinfo=0",
                                "https://www.youtube.com/embed/_df8tHFOxgg?rel=0&amp;showinfo=0",
                                "https://www.youtube.com/embed/BRvfZmwwHF0?rel=0&amp;showinfo=0"])


if __name__ == '__main__':
    unittest.main()
