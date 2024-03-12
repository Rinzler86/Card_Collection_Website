# App Id (Client ID) =  zebduffe-Collecti-SBX-a21dfce92-05537821
# Dev ID = 4d01b1f5-879d-4661-a1eb-7677146782a5
# Cert ID (Client Secret) = SBX-21dfce92df88-5681-4b87-8bb3-73e8

import requests
import json

# Your credentials
app_id = 'zebduffe-Collecti-SBX-a21dfce92-05537821'

# eBay Finding API endpoint for production
endpoint = 'https://svcs.ebay.com/services/search/FindingService/v1'

# Prepare the request parameters
params = {
    'OPERATION-NAME': 'findItemsByKeywords',
    'SERVICE-VERSION': '1.0.0',
    'SECURITY-APPNAME': app_id,
    'RESPONSE-DATA-FORMAT': 'JSON',
    'keywords': '',
}

# Make the GET request
response = requests.get(endpoint, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response
    data = response.json()
    print(data)
else:
    print(f'Error: {response.status_code}, {response.text}')

payload = json.dumps({
   "findItemsByKeywordsRequest": {
      "@xmlns": "https://www.ebay.com/marketplace/search/v1/services",
      "keywords": "harry potter phoenix"
   }
})

# Prepare the request headers
headers = {
    'X-EBAY-SOA-SECURITY-APPNAME': app_id,
    'X-EBAY-SOA-OPERATION-NAME': 'findItemsByKeywords',
    'X-EBAY-SOA-SERVICE-VERSION': '1.0.0',
    'X-EBAY-SOA-RESPONSE-DATA-FORMAT': 'JSON',
    'Content-Type': 'application/json',
}

# Make the POST request
response = requests.post(endpoint, data=payload, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response
    data = response.json()
    print(data)
else:
    print(f'Error: {response.status_code}, {response.text}')