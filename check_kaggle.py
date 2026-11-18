import requests
import re

# Navigate to Kaggle and check GPU availability
r = requests.get('https://www.kaggle.com', timeout=15)
print(f"Kaggle main: {r.status_code}")
print(f"Content length: {len(r.text)}")

# Look for notebook creation options
if r.status_code == 200:
    content = r.text
    # Find accelerator or GPU related links
    if 'accelerator' in content.lower():
        print("Accelerator-related content found")
    else:
        print("No explicit accelerator links found in dashboard")
    
    # Find links to new notebook creation
    links = re.findall(r'href=["\']([^"\']+)["\']', content)
    for link in links:
        if 'notebook' in link.lower():
            print(f"  Found notebook link: {link}")

print("\nNote: Kaggle GPU check requires running a notebook with accelerator")
print("The exact GPU (T4/P100) depends on Kaggle's current allocation.")
