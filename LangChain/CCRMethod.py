import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()


pdf_dir = "./files"

# 1. Load PDFs
loader = DirectoryLoader(
    path=pdf_dir,
    glob="company.pdf",
    loader_cls=PyPDFLoader,
    show_progress=True,
)

documents = loader.load()

if not documents:
    print("⚠️ No documents were loaded. Check if the directory contains PDF files.")
    raise SystemExit(0)

print(f" Metadata:\n{documents[0].metadata}\n")

total_pages = sum(doc.metadata.get("total_pages", 1) for doc in documents)
print(f"\n📊 Total pages: {total_pages}")

# 2. Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)
chunks = text_splitter.split_documents(documents)
print(f"📄 Total chunks created: {len(chunks)}")

# 3. Embed + store in Chroma
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorStore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",  # omit this arg for an in-memory store
)

print(f"✅ Vector store built with {vectorStore._collection.count()} vectors")

# 4. LLM — Gemini 2.5 Flash-Lite, used both as the CCR compressor and the answerer
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.5,
    api_key=os.environ.get("API_KEY"),
)

base_retriever = vectorStore.as_retriever(search_kwargs={"k": 4})
compressor = LLMChainExtractor.from_llm(llm)

ccr_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever,
)

answer_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant answering questions about a company using "
     "only the provided context. If the context doesn't contain the answer, "
     "say you don't have enough information — don't make anything up."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])


def answer_query(question: str) -> str:
    """Retrieve compressed, query-relevant context via CCR, then answer with Gemini."""
    compressed_docs = ccr_retriever.invoke(question)

    if not compressed_docs:
        return "No relevant information found in the document(s) for that question."

    context = "\n\n---\n\n".join(doc.page_content for doc in compressed_docs)
    messages = answer_prompt.format_messages(context=context, question=question)
    response = llm.invoke(messages)
    return response.content


if __name__ == "__main__":
 
    print("\nAsk questions about the document(s). Type 'exit' or 'quit' to stop.\n")
 
    while True:
        query = input("🔎 Question: ").strip()
 
        if not query:
            continue
        if query.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
 
        print(f"\n💬 Answer:\n{answer_query(query)}\n")


# import os
# from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import Chroma
# # from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings
# # from langchain_openai import OpenAIEmbeddings  # alternative if you have an OpenAI key

# pdf_dir = "./files"

# # 1. Load PDFs
# loader = DirectoryLoader(
#     path=pdf_dir,
#     glob="company.pdf",
#     loader_cls=PyPDFLoader,
#     show_progress=True,
# )

# documents = loader.load()

# if not documents:
#     print("⚠️ No documents were loaded. Check if the directory contains PDF files.")
# else:
#     print(f" Metadata:\n{documents[0].metadata}\n")

#     total_pages = sum(doc.metadata.get("total_pages", 1) for doc in documents)
#     print(f"\n📊 Total pages: {total_pages}")

#     # 2. Split into chunks
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200,
#         length_function=len,
#         is_separator_regex=False,
#     )
#     chunks = text_splitter.split_documents(documents)
#     print(f"📄 Total chunks created: {len(chunks)}")

#     # 3. Embed + store in Chroma
#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

#     vectorStore = Chroma.from_documents(
#         documents=chunks,
#         embedding=embeddings,
#         persist_directory="./chroma_db",  # omit this arg for an in-memory store
#     )

#     print(f"✅ Vector store built with {vectorStore._collection.count()} vectors")