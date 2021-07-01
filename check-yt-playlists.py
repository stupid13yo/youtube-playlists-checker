import time
import requests
from datetime import datetime
from tqdm import tqdm

s = requests.Session()

# User configuration
GCP_API_KEY = 'YOUR_API_KEY' # https://developers.google.com/youtube/v3/getting-started

# Script configuration
PLAYLIST_IDS_FILE = 'playlists.txt'
UNLISTED_IDS_BEFORE_2017_FILE = 'unlisted-before-17.txt'

# Read YouTube playlist IDs from file
with open(PLAYLIST_IDS_FILE) as f:
    playlistIds = f.read().strip().splitlines()

pageToken = ''

# Check each playlist
for playlistId in tqdm(playlistIds, 'Checking playlists', unit='playlists'):
    while True:
        url = f'https://www.googleapis.com/youtube/v3/playlistItems?key={GCP_API_KEY}&part=contentDetails,status&playlistId={playlistId}&maxResults=50&pageToken={pageToken}'
        res = requests.get(url)

        if res.status_code != 200:
            print('API returned non-200 status code, sleeping 3600 seconds')
            print(res.status_code)
            print(res.text)
            time.sleep(3600)

        data = res.json()
        
        unlistedVideos = []
        
        for item in data['items']:
            if item['status']['privacyStatus'] == 'unlisted':
                videoDate = datetime.strptime(item['contentDetails']['videoPublishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                if videoDate.year < 2017:
                    unlistedVideos.append(item['contentDetails']['videoId'])
        
        if len(unlistedVideos) > 0:
            with open(UNLISTED_IDS_BEFORE_2017_FILE, 'a+') as f:
                f.write('\n'.join(unlistedVideos) + '\n')

        try:
            pageToken = data['nextPageToken']
        except KeyError:
            pageToken = ''
            break

print(f'Unlisted video ids written to {UNLISTED_IDS_BEFORE_2017_FILE}')
