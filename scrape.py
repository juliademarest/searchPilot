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
for page_num in range(1, 20):
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

        # pull out core info, store in dict, append
        try:
            title = page.find("h1")
            speaker = page.find(class_="article-meta__author-bureau")
            audience = page.find(class_="article-meta__audience")
            location = page.find(class_="article-meta__location")
            date = page.find(class_="article-meta__publish-date")
            content = page.find(class_="entry-content")

            remarks_data = {
                "title": title.text,
                "speaker": speaker.text,
                "audience": audience.text,
                "location": location.text,
                "date": date.text,
                "content": content.text,
                "url": speech_link,
            }
            all_remarks.append(remarks_data)
            print(f"Sucessfully fetched: {speech_link}")

        except:
            print(f"Failed for {speech_link}")

        response.close()

        # some random sleep in here
        sleep(3 + random.uniform(-0.25, 0.25))

    # sleep extra between pages
    sleep(10 + random.uniform(-0.25, 0.25))

    print(f"Finished page {page_num}")

# write out
with open("remarks_more.json", "w") as outfile:
    json.dump(all_remarks, outfile)
