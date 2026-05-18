import urllib.request
import os

os.makedirs('database/Obama', exist_ok=True)

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

url1 = "https://upload.wikimedia.org/wikipedia/commons/8/8d/President_Barack_Obama.jpg"
print("Downloading database image...")
urllib.request.urlretrieve(url1, "database/Obama/1.jpg")

url2 = "https://upload.wikimedia.org/wikipedia/commons/e/e9/Official_portrait_of_Barack_Obama.jpg"
print("Downloading test image...")
urllib.request.urlretrieve(url2, "test_obama.jpg")

print("Download complete.")
