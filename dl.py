#!/usr/bin/env python3
# скачивалка c youtube, основанна на:
# by Siddharth Dushantha (sdushantha)
# Credits: https://git.io/JTPr9

import argparse
import json
import re
import requests


def sec2min(seconds):
    seconds = int(seconds)
    minutes =  (seconds//60)
    seconds = seconds - minutes*60
    return f"{minutes}min_{seconds}s"

def clear_file_name(string):
    return re.sub(r"[/\\*?:|\r\t\n]","",string)


def download(url):
    r = requests.get(url)
    html = r.text

    data = re.findall(r";ytplayer\.config = (.*);ytplayer\.web_player_context_config", html)[0]
    json_data = json.loads(data).get("args")
    player_response = json.loads ( json_data.get("player_response"))
    """
    player_response:
        responseContext <class 'dict'>
        playabilityStatus <class 'dict'>
        streamingData <class 'dict'>
        playerAds <class 'list'>
        playbackTracking <class 'dict'>
        captions <class 'dict'>
        videoDetails <class 'dict'>
        playerConfig <class 'dict'>
        storyboards <class 'dict'>
        microformat <class 'dict'>
        trackingParams <class 'str'>
        attestation <class 'dict'>
        adPlacements <class 'list'>
    """
    video_author = player_response["videoDetails"]["author"][:50]
    video_title = player_response["videoDetails"]["title"][:70]
    
    
    video_lenght = player_response["videoDetails"]["lengthSeconds"]
    video_lenght = sec2min(video_lenght)
    

    
    videoFormats = player_response.get("streamingData").get("formats")
    
    widths = [videoFormat.get("width") for videoFormat in videoFormats] # высокий битрейт не всегда лучше
    max_width = max(widths)
    bestQualityIndex = widths.index(max_width)
    
    height = videoFormats[bestQualityIndex].get("height")
    videoStreamURL = videoFormats[bestQualityIndex].get("url")
    qualityLabel = videoFormats[bestQualityIndex].get('qualityLabel')
    video_fps = videoFormats[bestQualityIndex].get('fps')
    mimeType = videoFormats[bestQualityIndex].get('mimeType')
    bitrate = videoFormats[bestQualityIndex].get('bitrate')
    audioChannels = videoFormats[bestQualityIndex].get('audioChannels')
    audioSampleRate = videoFormats[bestQualityIndex].get('audioSampleRate')

    print (f"""    автор:{video_author}
    название:{video_title}
    длина:{video_lenght}
    битрейт:{bitrate}
    w:{max_width}
    h:{height}
    qualyty:{qualityLabel}
    fps:{video_fps}
    audioChannels:{audioChannels}
    audioSampleRate:{audioSampleRate}
    mimeType:{mimeType}
    выбрано видео с шириной {max_width} из доступных {widths}
            """)
    print ("скачиваем...")
    #exit()
    try:
        r = requests.get(videoStreamURL)
    except requests.RequestException as e:
        print ("что-то не так cо скачиванием по ссылке, выходим...",e)
        print (videoFormats)
        exit()
    rawData = r.content

    filename = clear_file_name (f"{video_author}_{video_title}_({video_lenght})_({max_width}px).mp4")
    with open(filename, "wb") as f:
        f.write(rawData)

    print(f"Finished downloading    [ {filename} ]")

def main():
    parser = argparse.ArgumentParser(description="YouTube Downloader")
    parser.add_argument("url", help="URL to the YouTube video")
    args = parser.parse_args()
    download(args.url)
    

if __name__ == "__main__":
    main()