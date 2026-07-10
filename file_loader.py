from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("filepdf.pdf")
documents = loader.load()

print(f"Actual Data:\n{documents[0].page_content}\n")
print(f"Meta Data:\n{documents[0].metadata}\n")