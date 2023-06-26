# %%

# imports
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# %%
# load data - created in scrape.py
with open("data/clean/secretary-publicremarks.json", "r") as f:
    data = json.load(f)

# pull out text splitter from langchain
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

# loop for splitting text sections and copying metadata
texts = []
expanded_dicts = []
for remarks_dict in data:
    # split into paragraphs
    text = remarks_dict["secretary"].split("\n")
    del remarks_dict["secretary"]

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
#embeddings = OpenAIEmbeddings()
#vectordb = Chroma.from_texts(texts, embeddings, metadatas=expanded_dicts)
retriever = vectordb.as_retriever(search_kwargs={"k": 5})

# %%
# very simple example query - just return related docs
query = "Assume all text is from public remarks by the Secretary of State. What has the Secretary said about China?"
docs = retriever.get_relevant_documents(query)

#%%
# more complicated query - return descriptive paragraph with sources
query = "What has the Secretary said about AI? Use quotes from the provided text in your response."

chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=ChatOpenAI(temperature=0), retriever=retriever
)
result = chain({"question": query})
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")

# %%
# Increasing complicated query - evaluate change over time
# query = "Describe the differences between each speech given by the Secretary about AI"
# query = "How does the Secretary describe the use of AI in other countries? Cite which countries he discusses."
query = "How has the Secretary's view of AI changed over time?"
chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=ChatOpenAI(temperature=0), retriever=retriever
)
result = chain({"question": query})
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
# %%
query = "technology and AI "
docs = retriever.get_relevant_documents(query)

# %%
# Testing summarization
# Could probably move this into a separate script, but kept here
# now to easily take advantage of the docs. Renamed to docs_summ
# in order to not mess up the code above

# Prep documents
#TODO: picked 5, need to understand why
docs_summ = [Document(page_content=t) for t in texts[:5]]
llm = ChatOpenAI(temperature=0)

# Get basic summary
chain = load_summarize_chain(llm, chain_type="map_reduce")
chain.run(docs_summ)
#%%