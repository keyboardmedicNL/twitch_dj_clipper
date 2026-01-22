# what does it do?
runs locally and saves timestamps to a file trough a !clip command only accessable to mods and the broadcaster

after stream you run the clip generator and point it to your clips timestamp file and to the corresponding locally recorded vod and it will create clips at the timestamp with a set time, or alternativly, tell it to use the last files in both folders to run automagicly

the clips will be sorted in folder by creator in the ```clips``` folder in the root of the project

# how to run:
1. install uv https://docs.astral.sh/uv/getting-started/installation/
2. copy the ```example_config.yaml``` and rename it to ```config.yaml```
3. adjust the values as need
```
bot_name: 'the username of your bot account'
oath_token: 'your_oath_token' #generated on first run of the script
channel: 'the username of the channel the bot should join'
twitch_api_id: "your twitch api id"
twitch_api_secret: "your twitch api secret"
clip_start_before_timestamp: 30 #seconds
total_clip_duration: 60 #seconds
metadata_artist: clipper #name added to the clip files metadata
vod_folder_path: "/path/to/your/vods/folder
output_file_type: "mp4"
allow_stick: True # wether or not to allow the !stick command
```
4. run the twitch chat bot with the following command in the root of the project ```uv run main.py```
5. when you are ready to generate your clips run the following command in the root of the project ```uv run generate_clips.py```
* alternativly you can run the appropriate ```start twitchbot``` or ```start clip generator``` files for your os

A docker image is also available at ```keyboardmedic/twitch_dj_clipper:latest```

you can run it with
```
docker run -it -d --name twitch_dj_clipper -v "/path/to/your/configs":/usr/src/app/config -v "path/to/your/clip_timestamps":"/usr/src/app/clip timestamps" -v "path/to/your/clips":"/usr/src/app/clips" -v "path/to/your/vods":"/usr/src/app/vods" keyboardmedic/twitch_dj_clipper:nightly
```

# wip
currently no way exsists of running the clip generator in docker, will be added later