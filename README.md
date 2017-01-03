# Site Mapper

A collection of tools and services to facilitate mapping of large gov website

#### Note on depreciated repo

the [epa](https://github.com/edgi-govdata-archiving/epa) repo is now depreciated

## sitemapper.py

crawls a website and produces an xml sitemap.

the domain is obtainable via web service or cli paramater

csv and json versions are created from the xml sitemap

a zip archive is created containing xml, csv and json files

the zip file is uploaded to a cloud server

## Usage

### CLI mode

`python3 sitemapper.py www.domain.gov`

### POLL mode
`python3 sitemapper.py`

domain will be obtained from a [webservice](http://openciti.ca/cgi-bin/peek)

----

## Submodules

### cloning

use --recursive when cloning into this repo


## python-sitemap

A fork of https://github.com/c4software/python-sitemap

Was forked to preserve the current state of the code

Before the fork was made, a pull request to add GPL 3.0 was accepeted by c4software


### sitemap-redis

simple cgi to interact with a redis server

sites can be nominated then pulled and submitted

goal is to facilitate more cost effective off-cloud proccessing


### sitemap-web

>web views  TODO http://openciti.ca/archiving

>site nomination

>view mapping activity

>interact with complete site maps

>serve raw xml, csv or json data

>link to archived data and docs

# Licence

[GPL 3.0](http://www.gnu.org/licenses/gpl.txt)
