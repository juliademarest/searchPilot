# %%
import os
import json
import pandas as pd
import re
import unicodedata

# Define the folder path
folder_path = "data/raw"

# Get the list of files in the folder
file_list = os.listdir(folder_path)

all_remarks = []
# Iterate over each file
for file_name in file_list:
    # Construct the file path
    file_path = os.path.join(folder_path, file_name)

    # Read the JSON file
    with open(file_path, "r") as file:
        # Load the JSON data
        json_data = json.load(file)
        all_remarks.extend(json_data)


# from json to df, drop duplicates
remarks_data = pd.DataFrame(all_remarks)
remarks_data = remarks_data.drop_duplicates()

# small clean up, including unicode stripping
remarks_data["title"] = remarks_data["title"].str.strip()
remarks_data["content"] = remarks_data["content"].fillna("")
remarks_data["content"] = remarks_data["content"].apply(
    lambda x: unicodedata.normalize("NFKD", x)
)

# define regex pattern for matching names and colons like
# FOREIGN MINISTER JOLY:, SECRETARY BLINKEN: etc.
pattern = r"([A-Z\s]+:)"


# define function for splitting conversations using regex
def split_conversations(text):
    result = re.split(pattern, text)[1:]
    conversational_turns = []

    for i in range(0, len(result), 2):
        section = {"speaker": result[i].strip(), "content": result[i + 1].strip()}
        conversational_turns.append(section)

    return conversational_turns


# split remarks into conversational turns by speaker
remarks_data["conversation"] = remarks_data["content"].apply(
    lambda x: split_conversations(x)
)

# pull out only points from Sec. Blinken
blinken_points = []
for row in remarks_data["conversation"]:
    select_sections = []

    # keep values only if from Sec. Blinken and
    # longer than 30 characters (removes a lot of
    # hello, thank you, please, etc.)
    for value in row:
        if (
            type(value) is dict
            and value["speaker"] == "SECRETARY BLINKEN:"
            and len(value["content"]) > 30
        ):
            select_sections.append(value["content"])

    if len(select_sections) > 0:
        all_points = "\n".join(select_sections)
        blinken_points.append(all_points)
    else:
        blinken_points.append("")

# add in points from the secretary, drop everything from other speakers
remarks_data["secretary"] = blinken_points
remarks_data = remarks_data[
    remarks_data["speaker"] == "Antony J. Blinken, Secretary of State"
]

# keep only useful columns
remarks_data = remarks_data[
    ["url", "title", "speaker", "audience", "location", "date", "secretary"]
]

remarks_data = remarks_data.fillna("")

# write out as JSON
remarks_data.to_json(
    "data/clean/secretary-publicremarks.json", orient="records", force_ascii=False
)

#

# %%
