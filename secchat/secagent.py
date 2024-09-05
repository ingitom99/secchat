import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def make_agent(
        path: str,
        api_key: str
        ):
    llm = OpenAI(
        model="gpt-4-turbo",
        api_key=api_key
        )
    data = SimpleDirectoryReader(input_dir=path).load_data()
    index = VectorStoreIndex.from_documents(data)
    query_engine = index.as_query_engine(
        chat_mode="best",
        llm=llm,
        verbose=True,
        similarity_top_k=5,
    )
    return query_engine

