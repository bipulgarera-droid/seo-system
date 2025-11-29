import requests

url = "https://www.nytarra.in/products/divine-spark-candle"

headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
}

try:
    print(f"Fetching {url} as Googlebot...")
    response = requests.get(url, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    
    content = response.text
    target = "Infused with powerful healing oils"
    
    if target in content:
        print(f"\nSUCCESS: Found '{target}' in raw response!")
        index = content.find(target)
        start = max(0, index - 100)
        end = min(len(content), index + 100)
        print(f"Context:\n...{content[start:end]}...")
        
        # Check if it's inside a script tag
        before = content[:index]
        last_script_start = before.rfind('<script')
        last_script_end = before.rfind('</script')
        
        if last_script_start > last_script_end:
            print("\nIt appears to be inside a <script> tag.")
        else:
            print("\nIt appears to be in HTML (or other tag).")
            
    else:
        print(f"\nFAILURE: '{target}' NOT FOUND in raw response.")
        print("Saving raw response to debug_raw_response.txt for inspection.")
        with open('debug_raw_response.txt', 'w') as f:
            f.write(content)

except Exception as e:
    print(f"Error: {e}")
