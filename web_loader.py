from langchain_community.document_loaders import WebBaseLoader

webloader = WebBaseLoader("https://www.amazon.in/LG-1920x1080-Anti-Glare-Virtually-Borderless/dp/B0FHXY7VZ5/?_encoding=UTF8&pd_rd_w=hH1cs&content-id=amzn1.sym.2d1ab0f0-8827-4bb3-885e-1f3ae355e022&pf_rd_p=2d1ab0f0-8827-4bb3-885e-1f3ae355e022&pf_rd_r=WRHBSAZ2ZSFA98YMKMX2&pd_rd_wg=zLZ6d&pd_rd_r=022355d2-108d-4f87-95a4-96f18b494956&ref_=pd_hp_d_btf_ls_gwc_pc_en2_")
documents = webloader.load()

print(f"✅ Total documents loaded: {len(documents)}")

if documents:
    print(f"📄 Content preview:\n{documents[0].page_content[:500]}...\n")
    print(f"📋 Metadata:\n{documents[0].metadata}\n")
else:
    print("⚠️ No content was loaded.")