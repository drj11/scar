SCAR READER Scraper
===================

Get the SCAR READER data in GHCN v3 format.

`inv.py` fetches the list of SCAR READER stations and generates
a `scar.inv` file (and a `scar.url` file which is a list of
places for `dat.py` to look).

`dat.py` fetches monthly average temperature data for each
station and produces a single `scar.dat` file.
