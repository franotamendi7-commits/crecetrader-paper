import requests

# Check Kaggle login status
r = requests.get('https://www.kaggle.com', timeout=15)
print(f"Kaggle main: {r.status_code}")
print(f"Content length: {len(r.text)}")

# Look for login/session indicators
content = r.text.lower()
if 'logout' in content or 'cerrar sesión' in content:
    print("User appears to be logged in")
elif 'login' in content or 'sign in' in content:
    print("User appears to be logged out")
else:
    print("Status unknown from dashboard")
