# IMPORTANT
this is a command line tool, if you are not comfortable using the command line this is not for you... I will not teach you how to use a command line.

# what does it do?
runs locally and saves timestamps to a file trough a ```!clip (clip title)``` command only accessable to mods and the broadcaster, wich will save a timestamp, the clip creators username and the title seperated by comma's to a txt file wich is called ```clips-(current date).txt```

after stream you run the clip generator and point it to your clips timestamp file and to the corresponding locally recorded vod and it will create clips at the timestamp with a set time, or alternativly, tell it to use the last files in both folders to run automagicly, it will then use ffmpeg to create clips without re-encoding with the set length as defined in the config. the clips will be sorted in folder by creator in the ```clips``` folder in the root of the project with the name ```(clip date)_(clip title)_(creator name)_(channel name)```

to get a link to the github in your chat you can use ```!getclip``` or to use the build in easter egg command you can use ```!stick```

# how to run:
1. copy the ```example_config.yaml``` and rename it to ```config.yaml```
2. adjusted the config as needed:
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
allow_stick: True # wether or not to allow the !stick command, a small easter egg wich returns a "<username> has a <random> cm stick"
quiet: False # the script will run without interacting with chat and only connect for debugging purposes
extra_params: "" # a string of extra ffmpeg parameters to use in the clip generation that will be inserted before the output file is defined in the ffmpeg command, the ffmpeg command included in the generate_clips is 'ffmpeg -i {{}} -ss {clip_start_time} -t {clip_duration} -metadata artist="{config.metadata_artist}" -metadata title="{file_title}" {config.extra_params} -c copy {{}}'
```
3. install ffmpeg https://ffmpeg.org/download.html (if not added to path you must add the ffmpeg binary in the root of the scripts folder)

## scripted run (recommended):
to run the main bot excecute the ```start_twitchbot``` file for your os. When you want to generate the clips execute the ```start_clip_generator``` file for your os (.sh for linux/mac, .bat for windows).

## manual setup
1. set up a python virtual enviroment ```python3 -m venv .venv```
2. install the required dependencies ``` pip install -r requirements ```
3. to run the main bot  ```python main.py```
4. to run the clip generator ```python generate_clips.py```
5. when done run ```deactivate``` to get out of the python virtual enviroment

A docker image is also available at ```keyboardmedic/twitch_dj_clipper:latest```

you can run it with
```
docker run -it -d --name twitch_dj_clipper -v "/path/to/your/configs":/usr/src/app/config -v "path/to/your/clip_timestamps":"/usr/src/app/clip timestamps" -v "path/to/your/clips":"/usr/src/app/clips" -v "path/to/your/vods":"/usr/src/app/vods" keyboardmedic/twitch_dj_clipper:nightly
```
or using a docker compose file
```
services:
  clipper:
    image: keyboardmedic/twitch_dj_clipper:latest
    volumes:
      - type: bind
        source: /path/to/your/config
        target: /usr/src/app/config
      - type: bind
        source: /path/to/your/clip_timestamps
        target: "/usr/src/app/clip_timestamps"
      - type: bind
        source: /path/to/your/clips
        target: "/usr/src/app/clips"
      - type: bind
        source: /path/to/your/vods
        target: "/usr/src/app/vods"
```

# wip
currently no way exsists of running the clip generator in docker easily, only the twitch chat bot will function, i plan on adding the functionality later on
