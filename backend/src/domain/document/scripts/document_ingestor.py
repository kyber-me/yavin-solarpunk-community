from argparse import ArgumentParser
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_text_splitters import MarkdownTextSplitter, RecursiveCharacterTextSplitter, TextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore #VectorStore #VectorStoreRetriever

from src.constants import BASE_KNOWLEDGE_PATH



def ingest_documents(p: str | list[str], use_vec_store: bool = False) -> BaseRetriever | None:
    # paths = [Path(d) for d in p if isinstance(p, list) else Path(d)]
    docs = []
    get_path = lambda x: Path(BASE_KNOWLEDGE_PATH / x)
    if isinstance(p, list):
        for d in p:
            docs.append(Document(get_path(d).read_text()))
    else:
        docs.append(Document(get_path(p).read_text()))


    # text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=100, chunk_overlap=50)
    # doc_splits = text_splitter.split_documents(docs)
    md_splitter = MarkdownTextSplitter.from_tiktoken_encoder(chunk_size=100, chunk_overlap=50)
    md_splits = md_splitter.split_documents(docs)

    for d in md_splits:
        print(d, end="\n\n")


    vectorstore: BaseRetriever | None = None
    if use_vec_store:
        vectorstore = InMemoryVectorStore.from_documents(md_splits, OpenAIEmbeddings()).as_retriever()


    return vectorstore


if __name__ == "__main__":
    import argparse

    parser = ArgumentParser()
    parser.add_argument(
        "--d",
        nargs="+",
        type=str,
        required=True
    )
    parser.add_argument(
        "--usevector",
        # type=bool,
        action="store_true"
    )
    # Pass the paths to the documents as arguments to the function script
    ingest_documents(parser.parse_args().d)