# Data-mining-project (Shufersal)
### By Samuel Lederman & Ofir Shein Lumbroso
___
>data-mining-project repo contains a package of files that enables the user to scrab the data 
from the online supermarket site of the Shufersal chain: https://www.shufersal.co.il/online/he/S 

to run the scraper, one should run main.py:
usage: main.py [-h] [-url URL] [-gl] [-all] [-c] [-dc] [-d] user password

positional arguments:
  user        user name to mySQL data server
  password    password to mySQL data server

optional arguments:
  -h, --help  show this help message and exit
  -url URL    specific category url from the "Shufersal" online site to parse
              and collect to the Shufersal database
  -gl         get subcategories links to parse and fill category table
  -all        get all links from category table, parse and fill "Shufersal"
              database
  -c          create "Shufersal" database
  -dc         delete existing "Shufersal" database and creating a new one
  -d          delete "Shufersal" database

NOTE: make sure no Shufersal site is open when running main.py
NOTE: the urls for the specific url option (-url) should be from the second sub category type, for example look at sub_links.png

The scraped data will be inserted to the "shufersal" database, ERD diagram at EER Diagram - second milestone.png
