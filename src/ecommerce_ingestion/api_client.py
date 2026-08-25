import requests

api_url = 'https://fakestoreapi.com'

response = requests.get(f'{api_url}/products/1')
print(response.json())