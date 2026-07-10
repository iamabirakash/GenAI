from langchain_community.document_loaders import WebBaseLoader
from urllib.parse import urlparse

url = "https://www.lpu.in/"

print(f"Fetching links from {url} using WebBaseLoader...")

# Initialize LangChain's WebBaseLoader
loader = WebBaseLoader(url)

# Scrape the page to get the BeautifulSoup object directly via the loader
soup = loader.scrape()

# Using a list as a stack named "links"
links = []

# Extract all links and push to "links" stack
for a_tag in soup.find_all('a', href=True):
    href = a_tag['href']
    
    # Handling absolute and relative URLs without using urljoin
    if href.startswith('http://') or href.startswith('https://'):
        full_url = href
    elif href.startswith('//'):
        full_url = 'https:' + href
    elif href.startswith('/'):
        full_url = "https://www.lpu.in" + href
    else:
        full_url = "https://www.lpu.in/" + href
        
    links.append(full_url)
    
print(f"Total links found: {len(links)}")

# Stack for valid links
valid_links = []

# Process links from the "links" stack
while links:
    current_link = links.pop()
    
    # Parse the URL
    parsed_url = urlparse(current_link)
    domain = parsed_url.netloc.lower()
    
    # Check if the domain is lpu.in or a subdomain of it
    if domain == 'lpu.in' or domain.endswith('.lpu.in'):
        valid_links.append(current_link)
        
print(f"\nTotal valid LPU subdomain links: {len(valid_links)}\n")
print("Printing valid links...\n")

# Print the results and contents from valid_links stack
while valid_links:
    link = valid_links.pop()
    print(f"\n{'='*50}\nURL: {link}\n{'='*50}")
    try:
        page_loader = WebBaseLoader(link)
        docs = page_loader.load()
        for doc in docs:
            content = doc.page_content.strip()
            # Displaying the first 1000 characters to prevent console flooding
            print(content[:1000] + ("...\n[Content Truncated]" if len(content) > 1000 else ""))
    except Exception as e:
        print(f"Failed to load {link}: {e}")