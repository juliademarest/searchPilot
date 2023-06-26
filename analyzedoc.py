
# %%
# imports
from langchain import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import AnalyzeDocumentChain
from langchain.docstore.document import Document
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Based on this documentation: https://python.langchain.com/docs/modules/chains/additional/analyze_document
# The AnalyzeDocumentChain can be used as an end-to-end to chain. This chain takes in a single document, 
# splits it up, and then runs it through a CombineDocumentsChain.
    

# This seems to require a .txt input. In an attempt to not break
# my computer, I copied and pasted this from the web and saved as
# txt. Better would be to webscrape probably... but I was on a plane
# and had zero faith that would go through
# Link: https://www.state.gov/secretary-antony-j-blinken-at-the-national-security-commission-on-artificial-intelligences-nscai-global-emerging-technology-summit/
# did not preprocess stop words, etc here, but likely isn't needed?

with open("data/clean/Blinken_AI_Speech_07_21.txt", "r") as f:
    data_txt = f.read()
#%%
llm = OpenAI(temperature=0)
summary_chain = load_summarize_chain(llm, chain_type="map_reduce")
summarize_document_chain = AnalyzeDocumentChain(combine_docs_chain=summary_chain)

# Running on just one doc as a test
summarize_document_chain.run(data_txt)

#%% 

### Testing Q&A with Analyze Document
qa_chain = load_qa_chain(llm, chain_type="map_reduce")
qa_document_chain = AnalyzeDocumentChain(combine_docs_chain=qa_chain)

query = "What did the Secretary say about secure supply chains?"
qa_document_chain.run(input_document = data_txt, question = query)


# %%
