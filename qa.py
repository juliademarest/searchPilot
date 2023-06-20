# %%

# imports
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# %%
# load data - created in scrape.py
with open("data/remarks.json", "r") as f:
    data = json.load(f)

# pull out text splitter from langchain
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

# loop for splitting text sections and copying metadata
texts = []
expanded_dicts = []
for remarks_dict in data:
    # split into paragraphs
    text = remarks_dict["content"].split("\n")
    del remarks_dict["content"]

    # for each paragraph
    for text_line in text:
        # make a copy of the original metadata (title, date, url, speaker, location)
        new_dict = remarks_dict.copy()

        # add a 'source' line - this is what the function will look for
        new_dict.update(
            {
                "source": f"{remarks_dict['title']} ({remarks_dict['date']}, {remarks_dict['url']})"
            }
        )

        # add paragraph to list, add metadata dict to list
        texts.append(text_line)
        expanded_dicts.append(new_dict)

# %%

# pull out OpenAI embeddings and create Chroma vector store of data with embeddings
embeddings = OpenAIEmbeddings()
docsearch = Chroma.from_texts(
    texts, embeddings, metadatas=expanded_dicts
).as_retriever()

# %%
# very simple example query - just return related docs
query = "What has been said about China?"
docs = docsearch.get_relevant_documents(query)

# more complicated query - return descriptive paragraph with sources
query = "What has the Secretary said about Ukraine?"

chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=ChatOpenAI(temperature=0), retriever=docsearch
)
result = chain({"question": query})
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
