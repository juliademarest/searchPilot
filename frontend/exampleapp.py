# This is a BAD thing to do, but this is half working
# but I might have hit the OpenAI limit, so just pushing for reference


# to open, open anaconda promt, cd to directory, 
# and run streamlit run exampleapp.py (no quotes)
# it wil open up in web browser or provide link

# pip install streamlit
#%%
import streamlit as st # import the Streamlit library
from langchain.chains import LLMChain, SimpleSequentialChain # import LangChain libraries
from langchain.llms import OpenAI # import OpenAI model
from langchain.prompts import PromptTemplate 
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
import os
#%%
# Add main title
st.title(" Using LangChain & OpenAI")

# Add a link to the Github repository that inspired this app
st.markdown("Example Use Case")
st.markdown("LangChain documentation: https://python.langchain.com/docs/get_started")

#%%
# Add in API Key
# My env is all messed up, so please ignore this bad thing to do
OPEN_API_KEY = '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'

#%%
# This loading data could probably be separated out into a different
# and called from here

# load data - created in scrape.py
with open("C:/Users/demar/Search Pilot/searchPilot/data/clean/secretary-publicremarks.json", "r") as f:
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

# Begin to create model
#%%
# pull out OpenAI embeddings and create Chroma vector store of data with embeddings
embeddings = OpenAIEmbeddings()
vectordb = Chroma.from_texts(texts, embeddings, metadatas=expanded_dicts)
retriever = vectordb.as_retriever(search_kwargs={"k": 5})

# %%

def generate_basic_response(input_text):
  chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=ChatOpenAI(temperature=0), retriever=retriever)
  result = chain({"question": input_text})
  #st.info(result)
  print(f"Answer: {result['answer']}")
  print(f"Sources: {result['sources']}")
#%%
# TO DO: Fix this b/c of retriever
def find_related_docs(input_text):
   global embeddings
   global vectordb
   global retriever
   docs = retriever.get_relevant_documents(input_text)
   #st.info(docs)
#%%
selection = st.radio("Select a type of response:",('Related Docs', 'Description'))

with st.form('my_form'):
  text = st.text_area("Enter your question")
  submitted = st.form_submit_button('Submit')
  if submitted:
    if selection == 'Related Docs':
        find_related_docs(text)
    elif selection == "Description":
        generate_basic_response(text)


#%%
text = "Assume all text is from public remarks by the Secretary of State. What has the Secretary said about China?"
find_related_docs(text)
# %%
