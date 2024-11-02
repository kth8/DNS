import re
import os
import sys
import socket
import requests
from duckduckgo_search import DDGS
from rich.console import Console
from openai import OpenAI
from ffmpeg import FFmpeg

console = Console()

def check_server_accessibility(host, port):
    try:
        with socket.create_connection((host, port), timeout=2):
            console.print(f"Edge-TTS server at {host}:{port} is accessible", style="bold green")
            return True
    except (socket.timeout, ConnectionRefusedError):
        console.print(f"Edge-TTS server at {host}:{port} is not accessible", style="bold red")
        sys.exit(1)

def remove_markdown(summary):
    cleaned_summary = re.sub(r'\*+', '', summary)
    cleaned_summary = re.sub(r'#+', '', cleaned_summary)
    return cleaned_summary

def replace_space_with_underscore(input_string):
    return input_string.replace(' ', '_')

def convert_summary(summary, host, port, name):
    mp3_file_path = f"{name}.mp3"
    client = OpenAI(api_key="null", base_url=f"http://{host}:{port}/v1")
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        response_format="mp3",
        input=summary
    ) as response:
        response.stream_to_file(mp3_file_path)
    console.print(f"Mp3 file saved to {mp3_file_path}", style="bold green")
    return mp3_file_path

def get_thumbnail_url(keywords):
    results = DDGS().images(keywords=keywords, region="wt-wt", size="Wallpaper", type_image="Photo", max_results=1)
    first_result = results[0]
    url = first_result['thumbnail']
    return url

def download_thumbnail(url, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        path = f"{file_name}.jpg"
        with open(path, 'wb') as file:
            file.write(response.content)
        console.print(f"Thumbnail saved {url} as {path}", style="bold green")
        return path

def generate_mp4(image_file, audio_file, output_file):
    ffmpeg = (
        FFmpeg()
        .option("y")
        .option("loop", 1)
        .input(image_file)
        .input(audio_file)
        .output(
            output_file,
            {
                "vf": "scale=640:480",
                "c:v": "libx264",
                "c:a": "aac",
                "b:a": "192k",
                "shortest": None
            }
        )
    )
    ffmpeg.execute()
    console.print(f"Combined {audio_file} and {image_file} into {output_file}", style="bold green")
    return output_file

def cleanup(mp3, jpg):
        os.remove(mp3)
        os.remove(jpg)
        console.print(f"Deleted {jpg} and {mp3}", style="bold green")

def main(summary, tts_host, tts_port, name):
        check_server_accessibility(tts_host, tts_port)
        clean_summary = remove_markdown(summary)
        joined_name = replace_space_with_underscore(name)
        mp3_file = convert_summary(clean_summary, tts_host, tts_port, joined_name)
        thumbnail_url = get_thumbnail_url(joined_name)
        thumbnail_path = download_thumbnail(thumbnail_url, joined_name)
        mp4 = generate_mp4(thumbnail_path, mp3_file, f"{joined_name}.mp4")
        cleanup(thumbnail_path, mp3_file)
        return mp4
