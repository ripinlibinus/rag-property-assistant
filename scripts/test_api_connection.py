"""Quick test script for MetaProperty API connection"""
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

api_url = os.getenv('METAPROPERTY_API_URL')
api_token = os.getenv('METAPROPERTY_API_TOKEN')

print(f'API URL: {api_url}')
print(f'Token: {api_token[:20]}...' if api_token else 'Token: NOT SET')

# Test connection
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {api_token}'
}

try:
    # Test 1: Health check
    print('\n--- Testing GET /api/health ---')
    response = httpx.get(f'{api_url}/api/health', headers=headers, timeout=10)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        print(f'Health: {response.json()}')
    
    # Test 2: Get listings (correct endpoint) with limit and longer timeout
    print('\n--- Testing GET /api/v1/listings?per_page=5 ---')
    response = httpx.get(
        f'{api_url}/api/v1/listings', 
        params={'per_page': 5},
        headers=headers, 
        timeout=60
    )
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        listings = data.get('data', [])
        total = len(listings)
        print(f'Success! Found {total} listings')
        
        if listings:
            listing = listings[0]
            print(f'\nFirst listing:')
            for key in ['id', 'title', 'name', 'price', 'property_type', 'type', 'city']:
                if key in listing:
                    print(f'  - {key}: {listing[key]}')
    else:
        print(f'Response: {response.text[:300]}')
        
except httpx.TimeoutException:
    print('Request timed out after 60 seconds')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')

print('\n--- Test Complete ---')
