import requests
def isvirus(path):
    API_KEY = '0559c6c1b798416ecefb8ee8da0a3c56dcbaf20aa3ce43e349165a2974079062'
    file_path = path

    with open(file_path, 'rb') as f:
        files = {'file': (file_path, open(file_path, 'rb'))}
        params = {'apikey': API_KEY}
        response = requests.post('https://www.virustotal.com/vtapi/v2/file/scan', files=files, params=params)


    if response.status_code != 200:
        print("Upload failed")
        exit()

    analysis_id = response.json()['scan_id']

    url = 'https://www.virustotal.com/vtapi/v2/file/report'
    params = {
        'apikey': API_KEY,
        'resource': analysis_id  # can be scan_id, sha1, sha256, or md5
    }

    while True:
        response = requests.get(url, params=params)

        # Check if response content is not empty and status code is 200
        if response.status_code != 200:
            print("Failed to get report or empty response, retrying...")
            continue

        try:
            data = response.json()
        except Exception as e:
            print(f"Failed to decode JSON: {e}")
            continue

        if data.get('response_code') == 1:
            malicious = data.get('positives', 0)
            total = data.get('total', 0)

            if malicious > 0:
                print(f"Virus detected! {malicious} / {total} engines flagged this file.")
                return True
            else:
                print("No virus detected.")
                return False
        else:
            print("Report not ready yet")
        



print(isvirus("C:\\Users\\berid\\Downloads\\DB.Browser.for.SQLite-v3.13.1-win32.msi"))