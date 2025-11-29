import requests
from bs4 import BeautifulSoup

url = "https://www.nytarra.in/products/mayakhel-playing-cards"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # DEBUG: Check if target exists BEFORE cleaning
        target = soup.find(class_='product__info-container')
        if target:
            print(f"DEBUG: Found 'product__info-container' BEFORE cleaning. Classes: {target.get('class')}")
        else:
            print("DEBUG: 'product__info-container' NOT FOUND in raw HTML.")
            
        # Remove unwanted elements BEFORE extraction
        # Expanded list of noise classes/ids
        noise_terms = ['nav', 'menu', 'sidebar', 'breadcrumb', 'footer', 'header', 'search', 'cart', 'login', 'popup', 'modal', 'newsletter', 'related', 'recommendation', 'instagram', 'social', 'cookie', 'announcement', 'art_of_intentional_living', 'swiper', 'slider', 'card_content', 'intentional_living']
        
        for unwanted in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript", "svg", "form", "button", "input"]):
            unwanted.decompose()
        
        # Remove elements matching noise terms
        elements_to_remove = []
        for element in soup.find_all(class_=lambda x: x and any(term in str(x).lower() for term in noise_terms)):
            # Protect main content wrappers
            classes = element.get('class', [])
            class_str = str(classes).lower()
            
            # Protect main layout containers
            if element.name == 'main' or 'main' in class_str or 'content-for-layout' in class_str:
                continue
                
            # Protect product info wrappers - be very specific
            if 'product' in class_str:
                if 'info' in class_str or 'detail' in class_str or 'description' in class_str or 'main' in class_str:
                     continue
                
            elements_to_remove.append(element)
        
        for element in elements_to_remove:
            try:
                element.decompose()
            except:
                pass
        
        # Debug: Print structure to see what's left after cleaning
        print("\nDEBUG: HTML Structure after cleaning:")
        def print_structure(element, depth=0):
            if element.name:
                classes = element.get('class', [])
                print(f"{'  ' * depth}<{element.name} class='{classes}'>")
                for child in element.children:
                    if child.name:
                        print_structure(child, depth + 1)
        
        if soup.body:
            print_structure(soup.body)
            
        # Try CSS Selectors instead
        print("\nDEBUG: Testing CSS Selectors...")
        found_containers = []
        for selector in ['.product-description', '.rte', '.product__description', '.short-description', '.product__info-container']:
            matches = soup.select(selector)
            print(f"Selector '{selector}': Found {len(matches)}")
            found_containers.extend(matches)
            
        print(f"Found {len(found_containers)} priority containers via CSS select.")

        # If no specific containers found, fall back to main/article
        if not found_containers:
             main_tag = soup.find('main') or soup.find('article') or soup.find('div', class_=['content', 'main-content', 'post-content', 'entry-content', 'article-content'])
             if main_tag:
                 found_containers = [main_tag]
        
        if found_containers:
            # Get paragraphs, headings, lists
            content_parts = []
            seen_text = set()
            
            for container in found_containers:
                # Exclude div/span unless they look like text blocks
                # We focus on semantic text tags
                for elem in container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'li']):
                    text = elem.get_text(separator=' ', strip=True)
                    
                    # Avoid very short snippets (often UI labels)
                    if text and len(text) > 20: 
                        # Deduplicate
                        if text not in seen_text:
                            content_parts.append(text)
                            seen_text.add(text)
                            print(f"EXTRACTED: {text[:50]}...")
            
            body_content = '\n\n'.join(content_parts)
        else:
            print("NO CONTAINERS FOUND - FALLBACK")
            # Fallback: get all paragraphs
            paragraphs = soup.find_all('p')
            content_parts = []
            seen_text = set()
            for p in paragraphs:
                text = p.get_text(separator=' ', strip=True)
                if len(text) > 20 and text not in seen_text:
                    content_parts.append(text)
                    seen_text.add(text)
            body_content = '\n\n'.join(content_parts)
            
        print(f"FINAL CONTENT LENGTH: {len(body_content)}")

except Exception as e:
    print(f"Error: {e}")
