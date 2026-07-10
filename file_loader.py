from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_core import documents
import os

pdf_dir = "./files"

loader = DirectoryLoader(
    path=pdf_dir,
    glob="*.pdf",
    loader_cls=PyPDFLoader,
    show_progress=True
)

documents = list(loader.lazy_load())
print(f"✅ Total documents loaded: {len(documents)}")

if documents:
    print(f"📄 First document content preview:\n{documents[0].page_content[:500]}...\n")
    print(f"📋 Metadata:\n{documents[0].metadata}\n")
    
    print("Loaded files:")
    for i, doc in enumerate(documents[:]):
        print(f"  {i+1}. {doc.metadata.get('source', 'Unknown')}")
    
    total_pages = sum(doc.metadata.get('total_pages', 1) for doc in documents)
    print(f"\n📊 Total pages: {total_pages}")
else:
    print("⚠️ No documents were loaded. Check if the directory contains PDF files.")