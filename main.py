import os
import sys
import argparse
import requests
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook
from duckduckgo_search import DDGS
from rich.console import Console
import tts

console = Console()
load_dotenv()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Summarize DuckDuckGo search results using Google Gemini.")
    parser.add_argument('search', help='Search term')
    parser.add_argument('-r', '--results', type=int, default=10, help='Number of results to fetch (Default: 10)')
    parser.add_argument('-p', '--prompt', action='store_true', help='Show prompt sent to LLM')
    return parser.parse_args()

def load_env_variables():
    api_key = os.getenv('google')
    webhook_url = os.getenv('webhook_url')
    tts_host = os.getenv('tts_host')
    tts_port = os.getenv('tts_port')
    system_instruction = os.getenv('duckduckgo_news_summary')
    if not (api_key and webhook_url and tts_host and tts_port and system_instruction):
        console.print(f"Unable to load environment variables", style="bold red")
        sys.exit(1)
    return api_key, webhook_url, tts_host, tts_port, system_instruction

def configure_api(api_key):
    genai.configure(api_key=api_key)

def create_model(model_name, system_instruction):
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config={"temperature": 0.8},
        system_instruction=system_instruction
    )

def fetch_news_headlines(keywords, num_results):
    results = DDGS().news(keywords=keywords, region="en-us", safesearch="off", timelimit="w", max_results=num_results)
    titles_and_bodies = []
    if results:
        for result in results:
            titles_and_bodies.append({
                'title': result['title'],
                'body': result['body']
            })
    else:
        console.print("No results found", style="bold red")
        sys.exit(1)
    return titles_and_bodies

def generate_summary(model, search, show_prompt, results):
    formatted_results = "\n".join([f"Title: {item['title']}\nBody: {item['body']}\n" for item in results])
    prompt = f"Provide a summary of these news headlines that are related to {search}:\n{formatted_results}"
    response = model.generate_content(
        [prompt],
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH
        }
    )
    if show_prompt:
        console.print(prompt, style="bold")
    return response.text

def send_to_discord_webhook(summary, webhook_url, mp4):
    summary_length = len(summary)
    if summary and summary_length < 2000:
        webhook = DiscordWebhook(url=webhook_url, content=summary)
        with open(mp4, "rb") as f:
            webhook.add_file(file=f.read(), filename=mp4)
        webhook.execute()
        console.print(f"Summary sent to Discord. Length: {summary_length} characters", style="bold green")
    else:
        console.print(f"Could not send to Discord. Summary length {summary_length} longer than 2000.", style="bold red")

def main():
    args = parse_arguments()
    api_key, webhook_url, tts_host, tts_port, system_instruction = load_env_variables()
    try:
        configure_api(api_key)
        model = create_model("gemini-1.5-flash-001", system_instruction)
        results = fetch_news_headlines(args.search, args.results)
        summary = generate_summary(model, args.search, args.prompt, results)
        mp4 = tts.main(summary, tts_host, tts_port, args.search)
        send_to_discord_webhook(summary, webhook_url, mp4)
    except Exception as e:
        console.print(f"An error occurred: {e}", style="bold red")
        sys.exit(1)

if __name__ == "__main__":
    main()
