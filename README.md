# searchPilot

playing around with GPT and LangChain for semantic seach applications over documents.

## to do

- [x] scrape public remarks from principals to use as data
- [x] build MVP functional semantic search
- [x] clean up text
  - [x] remove unicode markers
  - [x] remove extra tabs from titles
  - [x] figure out a way to remove remarks from non-State leaders [just the Secretary for now]
- [ ] test out custom prompts - something like: "You are an intelligent Q&A bot... The inputs you will get represent public remarks by the Secretary of State and other senior State Department officials. Please be specific about who made the remarks you refer to in your answers."

## quick start

`pip install -r requirements.txt`

add `OPENAI_API_KEY = "your_key_here"` to a .env file at the top level of the repository.

## helpful resources

- [LangChain documentation](https://python.langchain.com/docs/get_started)
- [basic end to end tutorial](https://www.youtube.com/watch?v=aywZrzNaKjs), explaining embeddings, vector stores, chains, agents, and more
- similar use cases:
  - [docsGPT](https://github.com/arc53/DocsGPT/tree/main)
  - [knowledgeGPT](https://github.com/mmz-001/knowledge_gpt/tree/main)
  - [example QA](https://gist.github.com/anis-marrouchi/79c6446db5582e554b14db43b6b3e01e)
