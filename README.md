SCAR READER Scraper
===================

Get the [SCAR READER](http://www.antarctica.ac.uk/met/READER/) data in
[GHCN-M v3](http://www.ncdc.noaa.gov/ghcnm/v3.php) format. SCAR
READER is a collection of meteorological data from Antarctica
(SCAR is the Scientific Committee on Antarctic Research).
GHCN-M, Global Historical Climatology Network Monthly, is a
collection of meteorological data covering the globe. It is well
known and well used, there are likely to be many programs that
understand the GHCN-M data format, hence there is some value in
providing other datasets, SCAR READER, in this format.

`inv.py` fetches the list of SCAR READER stations and generates
a `scar.inv` file (and a `scar.url` file which is a list of
places for `dat.py` to look).

`dat.py` fetches monthly average temperature data for each
station and produces a single `scar.dat` file.

Station Identifiers
===================

GHCN-M uses an 11-digit station identifier scheme of the form:

    CCCWWWWWNNN

Where CCC is a 3 digit "country" code (not always a country, for
example, 700 is Antarctica); WWWWW is a 5 digit WMO station
identifier (of the station or its nearest WMO station); and NNN
is a arbitrary small number (which is 000 for a WMO station
itself).

This package assigns identifiers of the form:

    799WWWWW000

Note that all of the stations in SCAR have WMO identifiers. 799
is a "country" code chosen not to clash with an code already
used by GHCN-M. Also note that some stations in SCAR may also
have data in GHCN-M (with the same WMO identifier).
