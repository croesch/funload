#!/usr/bin/env python3

import xml.etree.ElementTree as ElemT
import unittest
import os
import datetime

import funload


def get_test_file(testfile):
    return open(os.path.expanduser("test_funload_files/" + testfile), 'r')


def get_test_xml(testfile):
    return ElemT.parse(get_test_file(testfile))


def get_item(testfile):
    return get_test_xml(testfile).getroot().find('channel').find('item')


class MockConfig(funload.Config):
    files = {}

    def write(self, name, content):
        self.files[name] = content

    def get_last_build(self, name):
        return self.files[name]


class TestHornoxe(unittest.TestCase):
    def test_multiple_youtube_links(self):
        item = get_item("test_multiple_youtube_links")
        date = datetime.datetime(2007, 12, 5)

        urls = funload.item_node_parse(item, date)
        self.assertEqual(urls, ["https://www.youtube.com/embed/Vx-1LQu6mAE?rel=0&amp;showinfo=0",
                                "https://www.youtube.com/embed/_df8tHFOxgg?rel=0&amp;showinfo=0",
                                "https://www.youtube.com/embed/BRvfZmwwHF0?rel=0&amp;showinfo=0"])


class TestEmok(unittest.TestCase):
    def test_get_all_new_emok_video_pages__updates_config(self):
        config = MockConfig()
        xml = get_test_xml("test_emok_videofeed")
        config.write('emok', datetime.datetime(2007, 12, 5))

        funload.get_all_new_emok_video_pages(config, 'emok', xml)
        self.assertEquals(config.get_last_build('emok'), "Sun, 22 Mar 2015 11:50:52 +0000")

    def test_get_all_new_emok_video_pages(self):
        config = MockConfig()
        xml = get_test_xml("test_emok_videofeed")
        config.write('emok', datetime.datetime(2007, 12, 5))

        urls = funload.get_all_new_emok_video_pages(config, 'emok', xml)
        self.assertEqual(urls, ["http://www.emok.tv/own-content/monsterbumserin-iii.html",
                                "http://www.emok.tv/videos/the-walking-dead-russland-edition.html",
                                "http://www.emok.tv/videos/profi-fuellt-sein-zippo-nach.html",
                                "http://www.emok.tv/videos/frau-beim-staubsaugen.html",
                                "http://www.emok.tv/videos/betrunkene-fail-compilation-3.html",
                                "http://www.emok.tv/videos/piranhas-fuettern.html",
                                "http://www.emok.tv/videos/abheben-beim-rennen.html",
                                "http://www.emok.tv/videos/wiesel-will-spielen.html",
                                "http://www.emok.tv/own-content/racing-grannies.html",
                                "http://www.emok.tv/videos/varoufakis-und-der-stinkefinger.html",
                                "http://www.emok.tv/videos/too-many-zooz.html",
                                "http://www.emok.tv/videos/waschbaer-nimmt-ganz-behutsam-das-leckerli.html",
                                "http://www.emok.tv/videos/evolution-der-videospiele.html",
                                "http://www.emok.tv/videos/besoffen-und-auf-dem-weg-nach-hause.html",
                                "http://www.emok.tv/videos/betrunkenes-eichhoernchen.html",
                                "http://www.emok.tv/videos/photoshop-experten-probieren-photoshop-1-0-aus.html",
                                "http://www.emok.tv/videos/uptown-funk-auf-dem-laufband.html",
                                "http://www.emok.tv/videos/dragon-ball-z-light-of-hope.html",
                                "http://www.emok.tv/videos/salchichitas-envueltas-kochen.html",
                                "http://www.emok.tv/emo/emo-der-woche-309.html"])

    def test_extract_emok_video_urls_nourl(self):
        file = get_test_file("test_emok_nourl")

        urls = funload.extract_emok_video_urls(file)
        self.assertEquals(urls, [])

    def test_extract_emok_video_urls_oneurl(self):
        file = get_test_file("test_emok_oneurl")

        urls = funload.extract_emok_video_urls(file)
        self.assertEquals(urls, ["http://www.emok.tv/wp-content/2015/03/walkinddead.mp4"])


if __name__ == '__main__':
    unittest.main()
