#!/usr/bin/env python3

import html.parser
import urllib.request
import warnings
import xml.dom.minidom

class HTMLTableParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        dom = xml.dom.minidom.getDOMImplementation()
        self.doc = dom.createDocument(None, None, None)
        self.stack = [self.doc.createElement("root")]

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

        if tag in ("a", "table", "td", "th", "tr"):
            if tag == "table" or "table" in [
              el.tagName for el in self.stack]:
                new = self.doc.createElement(tag)
                for a, v in attrs:
                    new.setAttribute(a, v)
                self.stack[-1].appendChild(new)
                self.stack.append(new)

    def handle_endtag(self, tag):
        if not self.stack:
            return
        if tag in ("a", "table", "td", "th", "tr"):
            tos = self.stack[-1]
            if tos.tagName != tag:
                warnings.warn("ignoring end tag {!r}".format(tag))
                return
            self.stack.pop()

    def handle_data(self, data):
        if self.stack and self.stack[-1].tagName in ("a", "td", "th"):
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
    Converts a dict to a single line formatted the same way as
    the GHCN-M v3 inventory file (refer to
    ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/v3/README).
    The line, which is newline terminated, is returned as a
    string.
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
    return "{:107s}\n".format(formatted)

def ConvertTableToGHCNMInv(table, out):
    for i, row in enumerate(table):
        if i == 0:
            # Typically ID, Name, Latitude, Longitude, Height
            header = row[:5]
            continue
        d = dict(zip(header, row))
        out.write(ConvertSingleDict(d))

def tablify(html):
    p = HTMLTableParser()
    p.feed(html)
    table = []
    for row_node in p.stack[0].firstChild.childNodes:
        row = []
        for el in row_node.childNodes:
            el.normalize()
            if len(el.childNodes) == 1 and el.firstChild.nodeType == 3:
                cell = el.firstChild.data
            else:
                cell = list(el.childNodes)
            row.append(cell)
        table.append(row)
    return table

def make_urls(table, o):
    for i, row in enumerate(table):
        if i == 0:
            # Typically ID, Name, Latitude, Longitude, Height
            header = row
            tavg_idx = row.index("Temperature")
            id_idx = row.index("ID")
            continue
        # Get the cell in the Temperature column
        cell = row[tavg_idx]
        if not isinstance(cell, str):
            # extract the element that contains the text "All"
            all = [node for node in cell if
              node.nodeType != 3 and
              node.tagName == "a" and node.firstChild.data.strip() == "All"]
            if len(all) == 1:
                href = all[0].getAttribute("href")
                if href.endswith(".html"):
                    href = href[:-5] + ".txt"
                o.write("{} {}\n".format(row[id_idx], href))


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
    table = tablify(html_inv)
    with open("scar.inv", 'w') as o:
        ConvertTableToGHCNMInv(table, o)
    with open("scar.url", 'w') as o:
        make_urls(table, o)

if __name__ == '__main__':
    main()
