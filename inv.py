#!/usr/bin/env python3

import html.parser
import urllib.request
import warnings
import xml.dom.minidom

class HTMLTableParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.table = []
        dom = xml.dom.minidom.getDOMImplementation()
        self.doc = dom.createDocument(None, None, None)
        self.stack = [self.doc.createElement('table')]

    def handle_starttag(self, tag, attrs):
        # In the broken HTML we get, there are some missing
        # closing tags. So here, we close previous tags when we
        # see a <TR>.
        if tag == "tr" and "tr" in [el.tagName for el in self.stack]:
            while True:
                tag_name = self.stack[-1].tagName
                self.handle_endtag(tag_name)
                if tag_name == "tr":
                    break

        if tag in ("a", "td", "th", "tr"):
            self.stack.append(self.doc.createElement(tag))
            print(list(map(lambda x:x.tagName, self.stack)))

    def handle_endtag(self, tag):
        if tag in ("a", "td", "th", "tr"):
            tos = self.stack[-1]
            if tos.tagName != tag:
                warnings.warn("ignoring end tag {!r}".format(tag))
                return
            child = self.stack.pop()
            self.stack[-1].appendChild(child)
            print(list(map(lambda x:x.tagName, self.stack)))

    def handle_data(self, data):
        if self.stack[-1].tagName in ("a", "td", "th"):
            self.stack[-1].appendChild(self.doc.createTextNode(data))
        else:
            # :todo: check data is whitespace?
            pass

URL = "http://www.antarctica.ac.uk/met/READER/surface/stationpt.html"

def fetch():
    req = urllib.request.Request(url=URL)
    f = urllib.request.urlopen(req)
    html = f.read().decode('ascii')
    return html

def ConvertSingleDict(d):
    """
    Refer to ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/v3/README
    for format of GHCN-M v3 inventory file (aka metadata).
    """

    import re

    # A made up country code for the purposes of GHCN-M.
    # 700 is currently used for Antarctica and is the only
    # "country" in the 7xx series. We can't use 700 here (as we
    # will clash with genuine GHCN-M stations) but it makes sense
    # to use something in the 7xx range.
    country = '799'
    wmo = d['ID']
    id = "{}{}000".format(country, wmo)

    m = re.match(r'^(\d+\.?\d*)S$', d['Latitude'])
    assert m, d['Latitude']
    latitude = -float(m.group(1))

    m = re.match(r'^(\d+\.?\d*)(?:\s|\n)*([EW])$', d['Longitude'])
    assert m, d['Longitude']
    longitude = float(m.group(1))
    if m.group(2) == 'W':
        longitude = -longitude

    m = re.match(r'(\d+)m$', d['Height'])
    assert m
    stelev = float(m.group(1))

    formatted = "{} {:8.4f} {:9.4f} {:6.1f} {:30.30s}".format(
      id, latitude, longitude, stelev, d['Name'])

    assert len(formatted) == 68
    print("{:107s}".format(formatted))
    

def ConvertTableToGHCNMInv(table):
    for i, row in enumerate(table):
        if i == 0:
            # Typically ID, Name, Latitude, Longitude, Height
            header = row[:5]
            continue
        d = dict(zip(header, row))
        ConvertSingleDict(d)

def tablify(html):
    p = HTMLTableParser()
    p.feed(html)
    print(p.stack[0].toprettyxml())
    ConvertTableToGHCNMInv(p.table)

def main(argv=None):
    import sys

    if argv is None:
        argv = sys.argv
    arg = argv[1:]
    if len(arg) == 0:
        html_inv = fetch()
    else:
        with open(arg[0]) as f:
            html_inv = f.read()
    tablify(html_inv)

if __name__ == '__main__':
    main()
