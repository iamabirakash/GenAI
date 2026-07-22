import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

PERSIST_DIR = "./chroma_db"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
    print("Loading existing vector store...")
    vectorStore = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings,
    )
else:
    # Create new vector store
    print("Creating new vector store")
    loader = DirectoryLoader(
        path="./files",
        glob="company.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
    )
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    
    vectorStore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
    )
    print(f"Vector store created with {vectorStore._collection.count()} vectors")

# Setup LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.5,
    api_key=os.environ.get("API_KEY"),
)

# Create CCR retriever
base_retriever = vectorStore.as_retriever(search_kwargs={"k": 4})
compressor = LLMChainExtractor.from_llm(llm)
ccr_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever,
)

# Answer prompt
answer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant answering questions about a company using only the provided context. If you find the information then give the correct information but If the context doesn't contain the answer, say you don't have enough information — don't make anything up."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])

def answer_query(question):
    compressed_docs = ccr_retriever.invoke(question)
    if not compressed_docs:
        return "No relevant information found."
    context = "\n\n---\n\n".join(doc.page_content for doc in compressed_docs)
    messages = answer_prompt.format_messages(context=context, question=question)
    response = llm.invoke(messages)
    return response.content

# Query loop
print("\nAsk questions about the document(s). Type 'exit' or 'quit' to stop.\n")
while True:
    query = input("🔎 Question: ").strip()
    if not query:
        continue
    if query.lower() in ("exit", "quit"):
        print("Goodbye!")
        break
    print(f"\n💬 Answer:\n{answer_query(query)}\n")