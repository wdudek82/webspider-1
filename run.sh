#!/bin/bash

source "venv/bin/activate"

# example
# scrapy crawl webspider -a domain='onet.pl' -a url='wiadomosci.onet.pl'
scrapy crawl webspider -a domain="$1" -a url="$2"

deactivate