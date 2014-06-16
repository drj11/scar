#!/usr/bin/env python3

import html.parser
import urllib.request

class HTMLTableParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.table = []
        self.row = False
        self.cell = False

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.table.append([])
            self.row = True
        if tag in ("td", "th"):
            self.table[-1].append('')
            self.cell = True
        # :todo: handle A elements for the HREF.

    def handle_endtag(self, tag):
        if tag == "tr":
            self.row = False
        if tag in ("td", "th"):
            self.cell = False

    def handle_data(self, data):
        if not self.cell:
            return
        if data:
            self.table[-1][-1] += data

URL = "http://www.antarctica.ac.uk/met/READER/surface/stationpt.html"

req = urllib.request.Request(url=URL)
f = urllib.request.urlopen(req)
xhtml = f.read().decode('ascii')

p = HTMLTableParser()
p.feed(xhtml)

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

ConvertTableToGHCNMInv(p.table)
