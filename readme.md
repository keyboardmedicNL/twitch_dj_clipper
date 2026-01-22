# what does it do?
runs locally and saves timestamps to a file trough a ```!clip (clip title)``` command only accessable to mods and the broadcaster, wich will save a timestamp, the clip creators username and the title seperated by comma's to a txt file wich is called ```clips-(current date).txt```

after stream you run the clip generator and point it to your clips timestamp file and to the corresponding locally recorded vod and it will create clips at the timestamp with a set time, or alternativly, tell it to use the last files in both folders to run automagicly, it will then use ffmpeg to create clips without re-encoding with the set length as defined in the config. the clips will be sorted in folder by creator in the ```clips``` folder in the root of the project with the name ```(channel name)_(creator name)_(clip title)_(clip date)```

to get a link to the github in your chat you can use ```!getclip``` or to use the build in easter egg command you can use ```!stick```

# how to run:
1. install uv https://docs.astral.sh/uv/getting-started/installation/
2. install ffmpeg https://ffmpeg.org/download.html
3. copy the ```example_config.yaml``` and rename it to ```config.yaml```
4. adjust the values as need
```
bot_name: 'the username of your bot account all lowercase' 
oath_token: 'your_oath_token' #generated on first run of the script by following instructions in the terminal
channel: 'the username of the channel the bot should join all lowercase'
twitch_api_id: "your twitch api id"
twitch_api_secret: "your twitch api secret"
clip_start_before_timestamp: 90 #seconds, the amount of time to go back from the created timestamp to set the start of the clip
total_clip_duration: 180 #seconds, the total time in second of how long you want your final clip to be
metadata_artist: twitch_dj_clipper #name added to the clip files metadata
vod_folder_path: "/path/to/your/vods/folder" #path to your vods folder used for generating clips with the latest files automagicly
output_file_type: "mp4" #the file type you would like to get your clips in
allow_stick: True # wether or not to allow the !stick command, a small easter egg wich returns a "<username> has a <random> cm stick"
```
5. run the twitch chat bot with the following command in the root of the project ```uv run main.py```
6. when you are ready to generate your clips run the following command in the root of the project ```uv run generate_clips.py```
* alternativly you can run the appropriate ```start twitchbot``` or ```start clip generator``` files for your os

A docker image is also available at ```keyboardmedic/twitch_dj_clipper:latest```

you can run it with
```
docker run -it -d --name twitch_dj_clipper -v "/path/to/your/configs":/usr/src/app/config -v "path/to/your/clip_timestamps":"/usr/src/app/clip timestamps" -v "path/to/your/clips":"/usr/src/app/clips" -v "path/to/your/vods":"/usr/src/app/vods" keyboardmedic/twitch_dj_clipper:nightly
```
or using a docker compose file
```
version: '3'
services:
  clipper:
    image: keyboardmedic/twitch_dj_clipper:latest
    volumes:
      - type: bind
        source: /path/to/your/config
        target: /usr/src/app/config
      - type: bind
        source: /path/to/your/clip_timestamps
        target: "/usr/src/app/clip timestamps"
      - type: bind
        source: /path/to/your/clips
        target: "/usr/src/app/clips"
      - type: bind
        source: /path/to/your/vods
        target: "/usr/src/app/vods"
```

# wip
currently no way exsists of running the clip generator in docker, only the twitch chat bot will function, i plan on adding the functionality later on