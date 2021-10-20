#!/usr/bin/env python3
from html.parser import HTMLParser
import urllib.request
 
#Import HTML from a URL
url = urllib.request.urlopen("https://khaliltuban.co.uk")
html = url.read().decode()
url.close()

class Parse(HTMLParser):
    def __init__(self):
    #Since Python 3, we need to call the __init__() function of the parent class
        super().__init__()
        self.reset()
    #Defining what the method should output when called by HTMLParser.
    def handle_starttag(self, tag, attrs):
        # Only parse the 'anchor' tag.
        if tag == "a":
            for name,link in attrs:
                if name == "href" and link.startswith("http"):
                    print (link)


def test_fire():
    p = Parse()
    p.feed(html)
