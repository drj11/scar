#!/usr/bin/env python3

import urllib.request

MISSING=9999.0

def fetch(url):
    """
    Fetch a single SCAR temperature record from `url` and yield
    a series of (year, data) pairs, where data is a 12-element
    list.
    """
    req = urllib.request.Request(url=url)
    f = urllib.request.urlopen(req)
    return grok(f)

def grok(inp, MISSING=MISSING):
    for i, line in enumerate(inp):
        line = line
        if i == 0:
            header = line
            continue
        year = line[:4]
        data = []
        for s in range(4, 99, 8):
            m = line[s:s+8].strip()
            if m == "-":
                data.append(MISSING)
            else:
                data.append(float(m))
        yield (year, data)

def ghcnm_write(id, values, out):
    """
    `id` is the 11 character identifier.
    `values` is an iterator of (year, data) pairs.
    `out` is a writable file to which data in GHCN-M format is
    written.
    """

    def format_single(v):
        if v == MISSING:
            return "-9999   "
        # Make up a source flag of "f" for foundation.
        return "{:5.0f}  f".format(v*100)

    FORMAT = "{}{}TAVG" + ("{:8s}"*12) + "\n"
    ALL_MISSING = [MISSING]*12
    for year, data in values:
        if data == ALL_MISSING:
            continue
        data = tuple(format_single(d) for d in data)
        formatted_row = FORMAT.format(*((id, year) + data))
        out.write(formatted_row)

BASE_URL = "http://www.antarctica.ac.uk/met/READER/surface/"

def urls():
    """
    Open the scar.url file and yield each row as a (wmo, url)
    pair.
    """

    with open("scar.url") as f:
        for row in f:
            wmo, url = row.split()
            url = BASE_URL + url
            yield (wmo, url)

def main(argv=None):
    with open("scar.dat", "w") as o:
        for wmo, url in urls():
            id11 = "799{}000".format(wmo)
            ghcnm_write(id11, fetch(url), o)

if __name__ == '__main__':
    main()
