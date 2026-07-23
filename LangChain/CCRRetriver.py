import os
from pathlib import Path
from typing import Sequence

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.documents.compressor import BaseDocumentCompressor
from langchain.retrievers import ContextualCompressionRetriever


# --- Load PDF -----------------------------------------------------------
def load_pdf(pdf_path):
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")
    loader = PyPDFLoader(str(path))
    return loader.load()


# --- Get or create vector store ------------------------------------------
def get_or_create_vectorstore(persist_dir="./chroma_db", pdf_path="./files/company.pdf"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    if not os.path.isdir(persist_dir) or not os.listdir(persist_dir):
        print(f"⚙️ Loading and embedding PDF: {pdf_path}")
        documents = load_pdf(pdf_path)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            length_function=len,
        )
        split_docs = splitter.split_documents(documents)

        vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=embeddings,
            persist_directory=persist_dir,
        )
    else:
        print("📂 Loading existing vector store...")
        vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings,
        )
    return vectorstore


# --- Custom summarizing compressor ---------------------------------------
# ContextualCompressionRetriever requires a BaseDocumentCompressor, i.e.
# something with a compress_documents(documents, query) method. A plain
# LCEL chain (prompt | llm) doesn't satisfy that interface on its own, so
# we wrap it in a small class that does.
class SummarizingCompressor(BaseDocumentCompressor):
    llm: ChatGoogleGenerativeAI
    prompt: PromptTemplate

    class Config:
        arbitrary_types_allowed = True

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks=None,
    ) -> Sequence[Document]:
        if not documents:
            return []

        context = "\n\n---\n\n".join(doc.page_content for doc in documents)
        chain = self.prompt | self.llm
        summary = chain.invoke({"context": context}).content

        # Return as a single compressed Document, carrying source metadata
        # from the first retrieved chunk for traceability.
        return [Document(page_content=summary, metadata=documents[0].metadata)]

    async def acompress_documents(self, documents, query, callbacks=None):
        return self.compress_documents(documents, query, callbacks)


# --- Build pipeline --------------------------------------------------------
vectorstore = get_or_create_vectorstore()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)

base_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

summary_prompt = PromptTemplate(
    input_variables=["context"],
    template=(
        "You are a summarisation assistant. Condense the following "
        "retrieved passages into a short, factual summary (max 2 sentences):\n\n"
        "{context}\n\nSummary:"
    ),
)

compressor = SummarizingCompressor(llm=llm, prompt=summary_prompt)

# CCR retriever
compressed_retriever = ContextualCompressionRetriever(
    base_retriever=base_retriever,
    base_compressor=compressor,
)


# --- Answer function (without RetrievalQA) ---------------------------------
def answer_query(query):
    # 1. Retrieve compressed documents
    docs = compressed_retriever.invoke(query)

    if not docs:
        return "No relevant information found."

    # 2. Build context from compressed docs
    context = "\n\n---\n\n".join(doc.page_content for doc in docs)

    # 3. Create prompt
    prompt = f"""You are a helpful assistant answering questions about a company.
Use ONLY the context provided below. If the context doesn't contain the answer,
say you don't have enough information.

Context:
{context}

Question: {query}

Answer:"""

    # 4. Get response
    response = llm.invoke(prompt)
    return response.content


# --- Query loop --------------------------------------------------------
if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        raise SystemExit("Set GOOGLE_API_KEY before running queries.")

    print("\n📚 Ask questions about the PDF. Type 'exit' or 'quit' to stop.\n")
    while True:
        query = input("🔎 Question: ").strip()
        if not query:
            continue
        if query.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        print(f"\n💬 {answer_query(query)}\n")