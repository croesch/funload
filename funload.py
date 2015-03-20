#!/usr/bin/env python3

import xml.etree.ElementTree as ElemT

import urllib
import os
from datetime import datetime


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
            print(item_node.find('link').text)
            item_pub_date_text = item_node.find('pubDate').text
            item_pub_date = datetime.strptime(item_pub_date_text, "%a, %d %b %Y %H:%M:%S +0000")
            if item_pub_date < last_build:
                print("\tOlder than last build..")
            else:
                print("\tMust be new..")
                for enclosure in item_node.iter('enclosure'):
                    url = enclosure.attrib['url']
                    filename = os.path.basename(url)
                    file_path = 'funload/' + filename
                    print("\tFound file '" + filename + "'")
                    if os.path.exists(file_path):
                        print("\talready exists.")
                    else:
                        print("\tdownloading..")
                        urllib.urlretrieve(url, file_path)
                        print("\tdone.")
    else:
        print("So no new version available..")


def hornoxe():
    download1('hornoxe', "http://hornoxe.com/feed/")


def orschlurch():
    download1('orschlurch', "http://www.orschlurch.net/kategorie/videos/feed/")


def youtube(link):
    if link.find("?") != -1:
        link = link[:link.find("?")]
    print("\tFound youtube video [" + link + "]")
    os.system("youtube-dl -q -o 'funload/%(id)s.%(ext)s' " + link + " > /dev/null 2>&1")


def totgelacht():
    f = config_file('totgelacht', 'r')
    last = f.readline().rstrip('\n')
    f.close()
    print("Last read link was " + last)

    print("Fetching..")
    rss_text = urllib.urlopen("http://www.totgelacht.com/rss2.php")
    print("Parsing..")
    root = ElemT.parse(rss_text).getroot()
    channel = root.find('channel')

    number = 1
    for item_node in channel.iter('item'):
        current = item_node.find('link').text
        print("{}: {}".format(number, current))
        if current == last:
            print("\tThis was the last read item.")
            break
        else:
            if number == 1:
                print("\tStoring the link.")
                f = config_file('totgelacht', 'w')
                f.write(current)
                f.close()

            content = urllib.urlopen(current).read()
            youtube_marker1 = "'file': 'http://www.youtube"
            youtube_marker2 = 'value="http://www.youtube'
            youtube_marker3 = 'src="http://www.youtube'
            if content.find(youtube_marker1) != -1:
                content = content[content.find(youtube_marker1) + 9:]
                content = content[:content.find("'")]
                youtube(content)
            elif content.find(youtube_marker2) != -1:
                content = content[content.find(youtube_marker2) + 7:]
                content = content[:content.find('"')]
                youtube(content)
            elif content.find(youtube_marker3) != -1:
                content = content[content.find(youtube_marker3) + 5:]
                content = content[:content.find('"')]
                youtube(content)
            else:
                prefix = "'file': '"
                pos = content.find(prefix)
                if pos != -1:
                    content = content[pos + len(prefix):]
                    content = content[:content.find("'")]
                    url = "http://www.totgelacht.com/content/" + content
                    filename = os.path.basename(url)
                    file_path = 'funload/' + filename
                    print("\tFound file '" + filename + "'")
                    if os.path.exists(file_path):
                        print("\talready exists.")
                    else:
                        urllib.urlretrieve(url, file_path)
                else:
                    print("\tSeems to be neither youtube nor a video..")
        number += 1


hornoxe()
orschlurch()
totgelacht()
