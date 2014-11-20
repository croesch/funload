#!/usr/bin/env python3

import xml.etree.ElementTree as ET

import urllib
import sys, os
from datetime import datetime, time, date

def configFile(project, mode):
    return open(os.path.expanduser("~/.funload/" + project), mode)

def download1(project, address):
    f = configFile(project, 'r')
    lastBuild = datetime.strptime(f.readline().rstrip('\n'), "%a, %d %b %Y %H:%M:%S +0000")
    f.close()
    print("Last read build was at " + lastBuild.isoformat())

    print("Fetching..")
    rsstext = urllib.urlopen(address)
    print("Parsing..")
    root = ET.parse(rsstext).getroot()
    channel = root.find('channel')

    currentBuildText = channel.find('lastBuildDate').text
    currentBuild = datetime.strptime(currentBuildText, "%a, %d %b %Y %H:%M:%S +0000")
    print("Current build is from " + currentBuild.isoformat())

    if currentBuild > lastBuild:
        print("Storing current build time.")
        f = configFile(project, 'w')
        f.write(currentBuildText)
        f.close()

        for item_node in channel.iter('item'):
            print(item_node.find('link').text)
            itemPubDateText = item_node.find('pubDate').text
            itemPubDate = datetime.strptime(itemPubDateText, "%a, %d %b %Y %H:%M:%S +0000")
            if itemPubDate < lastBuild:
                print("\tOlder than last build..")
            else:
                print("\tMust be new..")
                for enclosure in item_node.iter('enclosure'):
                    url = enclosure.attrib['url']
                    filename = os.path.basename(url)
                    filepath = 'funload/' + filename
                    print("\tFound file '" + filename + "'")
                    if os.path.exists(filepath):
                        print("\talready exists.")
                    else:
                        print("\tdownloading..")
                        urllib.urlretrieve(url, filepath)
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
    f = configFile('totgelacht', 'r')
    last = f.readline().rstrip('\n')
    f.close()
    print("Last read link was " + last)

    print("Fetching..")
    rsstext = urllib.urlopen("http://www.totgelacht.com/rss2.php")
    print("Parsing..")
    root = ET.parse(rsstext).getroot()
    channel = root.find('channel')

    number = 1
    for item_node in channel.iter('item'):
        current = item_node.find('link').text
        print("{}: {}".format(number ,current))
        if(current == last):
            print("\tThis was the last read item.")
            break
        else:
            if number == 1:
                print("\tStoring the link.")
                f = configFile('totgelacht', 'w')
                f.write(current)
                f.close()

            content = urllib.urlopen(current).read()
            youtubeMarker1 = "'file': 'http://www.youtube"
            youtubeMarker2 = 'value="http://www.youtube'
            youtubeMarker3 = 'src="http://www.youtube'
            if content.find(youtubeMarker1) != -1:
                content = content[content.find(youtubeMarker1) + 9:]
                content = content[:content.find("'")]
                youtube(content)
            elif content.find(youtubeMarker2) != -1:
                content = content[content.find(youtubeMarker2) + 7:]
                content = content[:content.find('"')]
                youtube(content)
            elif content.find(youtubeMarker3) != -1:
                content = content[content.find(youtubeMarker3) + 5:]
                content = content[:content.find('"')]
                youtube(content)
            else:
                prefix = "'file': '"
                pos = content.find(prefix)
                if pos != -1:
                    content = content[pos + len(prefix):]
                    content = content[:content.find("'")]
                    url = "http://www.totgelacht.com/content/" +    content
                    filename = os.path.basename(url)
                    filepath = 'funload/' + filename
                    print("\tFound file '" + filename + "'")
                    if os.path.exists(filepath):
                        print("\talready exists.")
                    else:
                        urllib.urlretrieve(url, filepath)
                else:
                    print("\tSeems to be neither youtube nor a video..")
        number += 1

hornoxe()
orschlurch()
totgelacht()
