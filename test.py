import requests
import os

url = 'http://127.0.0.1:8000/boost_accuracy'
headers = {
    'Content-Type': 'application/json',
    'Authorization': os.getenv('ASSEMBLYAI_API_KEY')
}
data = {
    'transcript_id': '7d0e2c0d-a1ad-4f3d-b94e-2f355d311160',
    'domain': 'medical',
    'boost_level': 'high',
    # 'custom_instructions': ''
    # 'word_boost_list': ['glucagon'],
    'confidence_filter': 0.8
}

response = requests.post(url, headers=headers, json=data)

print(response.json()['original_transcript'])
print(response.json()['corrected_transcript'])
print(response.json()['usage_costs'])
print(response.json()['time_taken_seconds'])