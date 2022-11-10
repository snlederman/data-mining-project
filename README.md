# data-mining-project - by Samuel Lederman and Ofir Shein Lumbroso 

data-mining-project repo contains a package of files that enables the user to scrab the data 
from the online supermarket site of the Shufersal chain: https://www.shufersal.co.il/online/he/S 

As first step, the user should run the Getting_links.py script to collect an up to date links 
of all the subcategories inside the webside. --> all the links are collected to the shufersal_links.csv file.

In order to collect the data from one of the mentioned subcategories, the user need to run page_scraper.py python3 script:

page_scraper: 
the script takes an url* of one of the subcategories in the Shufersal site and returns the following attributes for each product in that category:
            - product name
            - price
            - price unit
            - container
            - supplier
            
* at this stage the subcategory url needs to be changed manually inside the script (under the variable "MAIN URL")


