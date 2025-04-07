   import requests

   def search_pypi(query):
       url = f"https://pypi.org/pypi/{query}/json"
       response = requests.get(url)
       if response.status_code == 200:
           data = response.json()
           print(f"Package: {data['info']['name']}")
           print(f"Version: {data['info']['version']}")
           print(f"Summary: {data['info']['summary']}")
       else:
           print("Package not found.")

   search_pypi("generativeai")