# SEAO Web Scraping Tool

## About this app

This application is a tool to webscrape listing data from [SEAO](https://seao.ca/). The user can specify search/save options in `arguments.py`.

## Use this app locally

Clone the repository:

```
$ git clone https://github.com/Watergeeks/exploration.git
```

If you had previously cloned this repository, redirect to the root folder and update as follows:

```
$ git pull
```

Redirect to the respective app directory:

```
$ cd apps/SEAO
```

Install or update the required packages:

```
$ pip install -r requirements.txt
```

### Update arguments

Open `arguments.py` in a text editor to make the following updates if desired:
- Insert login details:
    - `self.username`: The username required for logging into [SEAO](https://seao.ca/)
    - `self.password`: The password required for logging into [SEAO](https://seao.ca/)
- Insert search criteria:
    - `self.searchany`: e.g. `'"eau potable" "eaux usées"'`
    - `self.searchall`: e.g. `'traitement'`
    - `self.searchnone`: e.g. `''`
    - `self.searchUNSPSC`: e.g. `['40151500', '40150000']`
- Consider what data to scrape:
    - `self.fields`: Fields to include as columns in the saved csv e.g. `['link', 'title', 'type', 'contract_type', 'date_publication', 'date_conclusion', 'date_complaints', 'organization', 'address', 'class_code', 'class_name', 'category_code', 'category_name']`

### Update driver

Currently there are two Chrome drivers saved at `drivers/` for two operating systems (i.e. Mac and Windows). 

Depending on what operating system and version of Chrome you are working with, you may have to [redownload the appropriate chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) and save it in directory `drivers/`. 

To find out what version of Chrome you need, open a window in Chrome and go to *Help* -> *About Google Chrome*

### Scrape listings

Run the app to scrape listings found based on given search criteria:

```
$ python3 scrape_listings.py
```

Open `result_listings.csv` to see results.

## Errors

https://sites.google.com/a/chromium.org/chromedriver/downloads

## Resources

* [SEAO](https://seao.ca/)
