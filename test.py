import requests

url = "https://captcha-api-lb4k.onrender.com/extract-captcha"
files = {'file': open('C:\Users\Lenovo\Desktop\case\test\abc.jpg', 'rb')}  # thay bằng file có chứa r3
response = requests.post(url, files=files)

print("Kết quả OCR là:", response.text)
