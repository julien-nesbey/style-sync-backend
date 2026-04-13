import requests

files = {'image': ('photo.jpg', b'dummy_content', 'image/jpeg')}
data = {'include_transparent_image': 'true'}
response = requests.post('http://127.0.0.1:8000/api/image/process', files=files, data=data)
print("Status:", response.status_code)
print("Body:", response.text)
