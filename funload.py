#!/usr/bin/env python3

import xml.etree.ElementTree as ElemT
import re
import urllib
import os
from datetime import datetime

namespaces = {'content': "http://purl.org/rss/1.0/modules/content/"}


def config_file(project, mode):
    return open(os.path.expanduser("~/.funload/" + project), mode)


def download1(project, address):
    f = config_file(project, 'r')
    last_build = datetime.strptime(f.readline().rstrip('\n'), "%a, %d %b %Y %H:%M:%S +0000")
    f.close()
    print("Last read build was at " + last_build.isoformat())

    print("Fetching..")
    rss_text = urllib.urlopen(address)
    print("Parsing..")
    root = ElemT.parse(rss_text).getroot()
    channel = root.find('channel')

    current_build_text = channel.find('lastBuildDate').text
    current_build = datetime.strptime(current_build_text, "%a, %d %b %Y %H:%M:%S +0000")
    print("Current build is from " + current_build.isoformat())

    if current_build > last_build:
        print("Storing current build time.")
        f = config_file(project, 'w')
        f.write(current_build_text)
        f.close()

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
    return urls


def download(url):
    if url.find("youtube"):
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


def hornoxe():
    download1('hornoxe', "http://hornoxe.com/feed/")


def orschlurch():
    download1('orschlurch', "http://www.orschlurch.net/kategorie/videos/feed/")


def main():
    hornoxe()
    orschlurch()


if __name__ == "__main__":
    main()
