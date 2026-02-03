import yaml
import logging

default_config = {
    "bot_name": '',
    "oath_token": '',
    "channel": '',
    "twitch_api_id": "",
    "twitch_api_secret": "" ,
    "clip_start_before_timestamp": 30,
    "total_clip_duration": 60,
    "metadata_artist": "twitch_dj_clipper",
    "vod_folder_path": "path/to/thingie"
}

# loads config from file
def load_config() -> dict:
    with open("config/config.yaml") as config_file:
        config_yaml = yaml.safe_load(config_file)
        merged_config = config_object({**default_config, **config_yaml})
    logging.debug("succesfully loaded config")       
    return(merged_config)

class config_object:
    def __init__(self, d=None):
        if d is not None:
            for key, value in d.items():
                setattr(self, key, value)