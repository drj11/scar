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

def id11_from_wmo(wmo):
    return "799{}000".format(wmo)

def from_urls():
    with open("scar.dat", "w") as o:
        for wmo, url in urls():
            id11 = id11_from_wmo(wmo)
            ghcnm_write(id11, fetch(url), o)

def from_file(f):
    import itertools

    with open("scar.url") as rows:
        wmo_map = [row.split() for row in rows]

    def find_wmo(name):
        for wmo, url in wmo_map:
            if name.startswith(url[:url.index(".")]):
                return wmo

    with open("scar.dat", "w") as o:
        for v,g in itertools.groupby(f, lambda x:x[0].isdigit()):
            if not v:
                # Single line consisting of station name.
                name = list(g)[0].strip()
                wmo = find_wmo(name)
            else:
                # Many data lines, one per year.
                id11 = id11_from_wmo(wmo)
                ghcnm_write(id11, grok(g), o)

def main(argv=None):
    import sys
    if argv is None:
        argv = sys.argv
    arg = argv[1:]
    if not arg:
        return from_urls()
    with open(arg[0]) as inp:
        return from_file(inp)

if __name__ == '__main__':
    main()
