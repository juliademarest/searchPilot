# %%
import requests
from time import sleep
import random
import json
from bs4 import BeautifulSoup

# need this header or the request gets blocked
header_dict = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

# list to store all results
all_remarks = []

# iterate over the pages (20 is an arbitrary limit)
for page_num in range(9, 25):
    # you know I love a print statement in the console
    print(f"Starting page {page_num}\n")

    # get the page of results of public remarks by State principals
    response = requests.get(
        f"https://www.state.gov/press-releases/page/{page_num}/?results=30&gotopage=&total_pages=25&coll_filter_year=&coll_filter_month=&coll_filter_speaker=&coll_filter_country=&coll_filter_release_type=452&coll_filter_bureau=&coll_filter_program=&coll_filter_profession=",
        headers=header_dict,
    )

    # parse html
    page = BeautifulSoup(response.text, "html.parser")

    # get a list of all the results on the page
    links_to_remarks = []
    list_items = page.find_all(class_="collection-result")

    # iterate over those results to get link to actual remarks
    for item in list_items:
        link = item.find("a")
        link = link["href"]
        links_to_remarks.append(link)

    # iterate over those results to go fetch text of remarks for each
    for speech_link in links_to_remarks:
        # get text of page, parses
        response = requests.get(
            speech_link,
            headers=header_dict,
        )
        page = BeautifulSoup(response.text, "html.parser")

        # elements we want to fetch
        elements = {
            "title": "featured-content__headline stars-above",
            "speaker": "article-meta__author-bureau",
            "audience": "article-meta__audience",
            "location": "article-meta__location",
            "date": "article-meta__publish-date",
            "content": "entry-content",
        }

        # base dict for storing metadata
        remarks_data = {
            "url": speech_link,
        }

        # try to find each metadata field in the html
        for metadata_field in elements.keys():
            try:
                value = page.find(class_=elements[metadata_field])
                remarks_data.update({metadata_field: value.text})
            except:
                print(f"Failed to find {metadata_field} for {speech_link}")

        all_remarks.append(remarks_data)
        print(f"Sucessfully fetched: {speech_link}")

        response.close()

        # some random sleep in here
        sleep(3 + random.uniform(-0.25, 0.25))

    # sleep extra between pages
    sleep(10 + random.uniform(-0.25, 0.25))

    print(f"Finished page {page_num}")
    with open(f"data/raw/remarks-page{page_num}.json", "w") as outfile:
        json.dump(all_remarks, outfile)

# %%
# write out
