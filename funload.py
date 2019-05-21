#!/usr/bin/env python3

import xml.etree.ElementTree as ElemT
import re
import urllib
import os
from datetime import datetime


namespaces = {'content': "http://purl.org/rss/1.0/modules/content/"}


def download1(config, project, address):
    last_build = config.get_last_build(project)
    print("Last read build was at " + last_build.isoformat())

    print("Fetching..")
    rss_text = urllib.urlopen(address)
    print("Parsing..")
    root = ElemT.parse(rss_text).getroot()
    channel = root.find('channel')

    current_build_text = channel.find('lastBuildDate').text.strip()
    current_build = datetime.strptime(current_build_text, "%a, %d %b %Y %H:%M:%S +0000")
    print("Current build is from " + current_build.isoformat())

    if current_build > last_build:
        print("Storing current build time.")
        config.write(project, current_build_text)

        for item_node in channel.iter('item'):
            for url in item_node_parse(item_node, last_build):
                download(url)
    else:
        print("So no new version available..")


def item_node_parse(item_node, last_build):
    urls = []

    print(item_node.find('link').text)
    item_pub_date_text = item_node.find('pubDate').text
    item_pub_date = datetime.strptime(item_pub_date_text, "%a, %d %b %Y %H:%M:%S +0000")
    if item_pub_date < last_build:
        print("\tOlder than last build..")
    else:
        print("\tMust be new..")
        for enclosure in item_node.iter('enclosure'):
            urls.append(enclosure.attrib['url'])
        for content in item_node.iterfind('content:encoded', namespaces=namespaces):
            for match in re.finditer('https?://(www)?\.youtube[^"\']*', content.text):
                urls.append(match.group(0))
            for match in re.finditer('SFYouTubePlayer.embedPlayer\("([^"\']*)', content.text):
                urls.append(match.group(1))
    return urls


def download(url):
    if url.find("youtube") != -1:
        link = url
        if link.find("?") != -1:
            link = link[:link.find("?")]
        print("\tFound youtube video [" + link + "]")
        os.system("youtube-dl -q -o 'funload/%(id)s.%(ext)s' " + link + " > /dev/null 2>&1")
    else:
        filename = os.path.basename(url)
        file_path = 'funload/' + filename
        print("\tFound file '" + filename + "'")
        if os.path.exists(file_path):
            print("\talready exists.")
        else:
            print("\tdownloading..")
            urllib.urlretrieve(url, file_path)
            print("\tdone.")


def get_all_new_emok_video_pages(config, project, xml):
    links = []

    last_build = config.get_last_build(project)
    print("Last read build was at " + last_build.isoformat())

    print("Parsing..")
    root = xml.getroot()
    channel = root.find('channel')

    current_build_text = channel.find('lastBuildDate').text.strip()
    current_build = datetime.strptime(current_build_text, "%a, %d %b %Y %H:%M:%S +0000")
    print("Current build is from " + current_build.isoformat())

    if current_build > last_build:
        print("Storing current build time.")
        config.write(project, current_build_text)

        for item_node in channel.iter('item'):
            print(item_node.find('link').text)
            item_pub_date_text = item_node.find('pubDate').text
            item_pub_date = datetime.strptime(item_pub_date_text, "%a, %d %b %Y %H:%M:%S +0000")
            if item_pub_date < last_build:
                print("\tOlder than last build..")
            else:
                links.append(item_node.find('link').text)
    else:
        print("So no new version available..")
    return links


def extract_emok_video_urls(file):
    urls = []

    for url_match in re.finditer("\"(http://[^\"]+\.mp4)\"", file.read()):
        urls.append(url_match.group(1))

    return urls


def hornoxe(config):
    download1(config, 'hornoxe', "http://hornoxe.com/feed/")


def orschlurch(config):
    download1(config, 'orschlurch', "http://www.orschlurch.net/kategorie/videos/feed/")


def emok(config):
    xml = ElemT.parse(urllib.urlopen("http://www.emok.tv/category/own-content/feed"))
    links = get_all_new_emok_video_pages(config, 'emok', xml)
    urls = []
    for link in links:
        urls.extend(extract_emok_video_urls(urllib.urlopen(link)))
    for url in urls:
        download(url)


def main():
    config = Config()
    hornoxe(config)
    orschlurch(config)
    emok(config)


class Config():
    def config_file(self, project, mode):
        return open(os.path.expanduser("~/.funload/" + project), mode)

    def get_last_build(self, project):
        f = self.config_file(project, 'r')
        last_build = datetime.strptime(f.readline().rstrip('\n'), "%a, %d %b %Y %H:%M:%S +0000")
        f.close()
        return last_build

    def write(self, project, content):
        f = self.config_file(project, 'w')
        f.write(content)
        f.close()


if __name__ == "__main__":
    main()
