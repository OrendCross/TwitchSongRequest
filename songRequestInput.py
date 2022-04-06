# songRequestInput.py
# Takes inputted YouTube, SoundCloud, or phrases and inserts relevant audio URLs into the queue database

import os.path, sqlite3, urllib.request, re, sys, codecs, requests, json
from Google import Create_Service
from bs4 import BeautifulSoup
from iso8601_duration import parse_duration

#YouTube API Info
YoutubeAPIKey = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

con = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'songRequest.db'))

# Global Variables 
youTubeURL 	= 'https://www.youtube.com/watch?v='
maxVideoSeconds = 300

# Return YouTube Video ID from search term(s)
def searchYoutube(searchQuery):
	search = searchQuery.replace(' ','+')
	html = urllib.request.urlopen('https://www.youtube.com/results?search_query=' + search)
	video_ids = re.findall(r'watch\?v=(\S{11})', html.read().decode())
	return video_ids[0]

# Return YouTube Video ID from URL
def getYouTubeID(Search):
	parseURL = urlparse(Search)
	if len(parseURL.query) > 0:
		videoID = parseURL.query.replace('v=', '')
	else:
		videoID = parseURL.path.replace('/', '')
	return videoID

# Get YouTube Information
def getYouTubeInfo(videoID):
	API =  requests.get('https://www.googleapis.com/youtube/v3/videos?id=' + videoID + '&key=' + YoutubeAPIKey + '&part=contentDetails,snippet')
	data = API.text
	return json.loads(data)

# Get SoundCloud title
def getSoundCloudInfo(url):
	html = urllib.request.urlopen(url)
	title = re.findall(r'<title>(.*?)<\/title>', html.read().decode())[0]
	title = title.replace(' | Listen online for free on SoundCloud', '')
	title = title.replace('<title>', '')
	title = title.replace('&quot;', '')
	title = title.replace('Stream ', '', 1)
	title = title.replace('Listen to ', '', 1)
	title = title.replace(' playlist online for free on SoundCloud', '')
	return title

# Return false if video is longer than 300 seconds
def checkVideoLength(durration):
	if parse_duration(durration).total_seconds() > maxVideoSeconds:
		return False
	return True

# Inserts songs and users into the SongDatabase
def insertIntoDB(Priority, TwitchUserID, Username, Title, URL):
	cur = con.cursor()
	cur.execute("INSERT OR REPLACE INTO Users VALUES (?, ?)", (TwitchUserID, Username))
	cur.execute("INSERT INTO Songs VALUES (?, ?, ?, ?, ?)", (Title, URL, 'Queued', Priority, TwitchUserID))
	con.commit()
	con.close()

# Checks SongDatabase for duplicate URLS in the active queue
def checkForDuplicates(URL):
	cur = con.cursor()
	cur.execute("SELECT COUNT(*) FROM Songs WHERE URL = ? AND Status = 'Queued'", (URL,))
	dupes = cur.fetchone()[0]
	if dupes > 0:
		return True
	else:
		return False

# Main
# Command:
# songRequestBot.py [Priority=0|1] [TwitchUserID] [TwitchUsername] [RequestURL/SearchTerm(s)]
#
# Result:
# Return (via print) message to be sent to chat
# Add song to SQLite DB
def main():
	if len(sys.argv) < 5:
		print('Usage: ' + sys.argv[0] + ' [Priority=0|1] [TwitchUserID] [TwitchUsername] [RequestURL/SearchTerm(s)]')
		sys.exit(1)
	
	# Priority = 0 | 1
	Priority = sys.argv[1]
	# TwitchUserID = Twitch UUID
	TwitchUserID = sys.argv[2]
	# TwitchUsername = Username
	TwitchUsername = sys.argv[3]
	# Search = SoundCloud or YouTube or phrase
	Search = sys.argv[4]
	for x in sys.argv[5:]:
		Search = Search + ' ' + x

	URL = ''
	Title = ''

	youtubeMatch = re.search(r'(?:.+?)?(?:\/v\/|watch\/|\?v=|\&v=|youtu\.be\/|\/v=|^youtu\.be\/|watch\%3Fv\%3D)([a-zA-Z0-9_-]{11})+', Search)
	soundCloudMatch = re.search(r'^(?:(https?):\/\/)?(?:(?:www|m)\.)?(soundcloud\.com|snd\.sc)\/(.*)$', Search)

	if youtubeMatch or soundCloudMatch:
		# If input is a YouTube Link
		if youtubeMatch:
			ID = youtubeMatch.group(1)
			videoInfo = getYouTubeInfo(ID)

			# If YouTube Link is invalid
			if videoInfo['pageInfo']['totalResults'] == 0:
				print('@' + TwitchUsername + ' Unable to add song to queue: link invalid!')
				return

			if not checkVideoLength(videoInfo['items'][0]['contentDetails']['duration']):
				print('@' + TwitchUsername + ' Request is not within the required length, 1 to 300 seconds')
				return

			URL = youTubeURL + ID
			Title = videoInfo['items'][0]['snippet']['title']

		# Else if input is a SoundCloud Link
		elif soundCloudMatch:
			if '/sets/' in Search:
				print('@' + TwitchUsername + ' You must request an individual SoundCloud link; not a set!')
				return

			URL = Search
			Title = getSoundCloudInfo(Search)

		else:
			# If input is a URL that does not get caught by the initial checks
			print('@' + TwitchUsername + ' Only valid YouTube or SoundCloud links are accepted!')
			return


	# Else input is something else (phrase, youtube VideoID, unsupported website, or gibberish)
	else:
		# Checking if YouTube Video ID
		IDCheck = re.search(r'(.*?)(^|\/|v=)([a-z0-9_-]{11})(.*)?', Search, flags=re.I|re.M)
		if IDCheck:
			videoInfo = getYouTubeInfo(IDCheck.group(3))
			if videoInfo['pageInfo']['totalResults'] != 0:
				URL = youTubeURL + IDCheck.group(3)
				Title = videoInfo['items'][0]['snippet']['title']

		else:
			ID = searchYoutube(Search)
			videoInfo = getYouTubeInfo(ID)
			URL = youTubeURL + ID
			Title = videoInfo['items'][0]['snippet']['title']

	if checkForDuplicates(URL):
		print('@' + TwitchUsername + ' This song is already in the Queue!')
		return

	insertIntoDB(Priority, TwitchUserID, TwitchUsername, Title, URL)
	print('@' + TwitchUsername + ' Added ' + Title + ' to the Queue')

	print('URL: ' + URL )
	print('Title: ' + Title )
	print('User: ' + TwitchUserID )

	#encoded_unicode = Title.encode("utf8")
	#f = open('H:\\My Drive\\MixItUp\\Files\\test.txt', "wb")
	#f.write(encoded_unicode)
	#f.close()

main()
