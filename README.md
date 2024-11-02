# Discord News Summarizer
This program uses DuckDuckGo to scrape news headlines related to your search term from the past week, sends it to Google Gemini for summarization, converts the summary to a mp4 file using text-to-speech server then send both text and audio versions to Discord via webhook.

Requirements:
 - Python3
 - FFmpeg
 - Docker
 - Google Gemini API key (free if you have a Google account): https://aistudio.google.com/app/apikey
 - Discord webhook URL: https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks

```
pip install -r requirements.txt
docker compose up -d
cp .env.example .env
```
edit the `.env` file with your API key and webhook URL then run:
```
$ python main.py github
Edge-TTS server at 127.0.0.1:5050 is accessible
Mp3 file saved to github.mp3
Thumbnail saved https://tse3.mm.bing.net/th?id=OIP.FZGVRUnLT0WHCUnE3lPNrwHaF7&pid=Api as github.jpg
Combined github.mp3 and github.jpg into github.mp4
Deleted github.mp3 and github.jpg
Summary sent to Discord. Length: 1457 characters
```
if everything works you should see something like this in your Discord channel: ![screenshot](./screenshot.png)
