import subprocess

import housey_logging

housey_logging.configure()

import logging
import sys
import os
import config_loader
import glob
import re

output_path = "clips"
clips_timestamp_files_path = os.path.join("clip timestamps","*")

def create_clips(input_file: str, output_file_type: str, list_of_clip_timestamps: list, clip_date:str):
    for i, clip_stamp in enumerate(list_of_clip_timestamps):
        
        clip_list = clip_stamp.split(",")
        username = sanitize_filename(clip_list[1])
        clip_title = clip_list[2].replace(" ", "-")
        file_title = f"{config.channel}_{username}_{clip_title}_{clip_date}"
        sanitized_name = sanitize_filename(file_title)
        
        output_file = os.path.join(output_path,username,f"{sanitized_name}.{output_file_type}")

        clip_start_time = timestamp_to_time_str(int(clip_list[0]) - int(config.clip_start_before_timestamp))
        clip_duration = timestamp_to_time_str(config.total_clip_duration)

        output_folder = os.path.join(output_path,username)
        os.makedirs(output_folder, exist_ok=True)

        command = (
            f'ffmpeg -i {{}} '
            f'-ss {clip_start_time} '
            f'-t {clip_duration} '
            f'-metadata artist="{config.metadata_artist}" '
            f'-metadata title="{file_title}" '
            f'-c copy {{}}'
            ).format(input_file, output_file)

        subprocess.call(command, shell=True)

def get_clip_timestamps(clips_file: str) -> list:
    clips_date = clips_file.split("-",1)
    clips_date = (clips_date[1].split(".")[0])
    with open(clips_file, 'r') as file:
        list_of_clip_timestamps = [line.rstrip() for line in file]
        logging.debug(f"list of clips retrieved from file = {list_of_clip_timestamps}")
        logging.debug(f"date extracted from clips file = {clips_date}")

    return(list_of_clip_timestamps, clips_date)

def sanitize_filename(name: str, replacement: str="_") -> str:
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', replacement, name)
    sanitized = sanitized.strip(" .")

    return sanitized if sanitized else "unnamed"

def wrap_string(user_input: str) -> str:
    user_input = user_input.strip("\"\'")

    if " " in user_input:
        user_input = f"'{user_input}'"

    return(user_input)

def get_parent_folder(user_input: str) -> str:
    if "/" in user_input or "\\" in user_input:
        if "/" in user_input:
            user_input = user_input.split("/")
        elif "\\" in user_input:
            user_input = user_input.split("\\")

        del user_input[-1]
        user_input = "/".join(user_input)

    user_input = wrap_string(user_input)

    return(user_input)

def y_or_n(user_input: str) -> bool:
    if user_input == "" or user_input.lower() == "y":
        return(True)
    else:
        return(False)

def build_path(file_path: str, file_name: str) -> str:
    return(os.path.join(file_path, file_name))

def timestamp_to_time_str(time_stamp) -> str:
    hours, remainder = divmod(time_stamp, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return time_str

def get_last_file_in_folder(folder_path: str) -> str:
    folder_path_path = os.path.expanduser(folder_path)
    folder_glob = glob.glob(folder_path_path)
    if len(folder_glob) == 0:
        raise RuntimeError(f"Folder {folder_path_path} is empty")

    return max(folder_glob, key=os.path.getctime)

def main():
    logging.info("starting twitch dj clipper")

    keep_going = True
    vod_file_parent = False
    clips_file_parent = False
    use_vod_parent = False
    use_clips_parent = False

    use_last_files = input(f"do you want to use the last created clips file and last created vod (Y) or n\n")
    use_last_files = y_or_n(use_last_files)

    if use_last_files:
        clips_file = get_last_file_in_folder(clips_timestamp_files_path)
        print(f"clip timestamp file to use = {clips_file}")

        list_of_clip_timestamps, clips_date = get_clip_timestamps(clips_file)

        input_file = get_last_file_in_folder(os.path.join(config.vod_folder_path,"*"))
        input_file = wrap_string(input_file)
        print(f"vod to use = {input_file} ")

        create_clips(input_file, config.output_file_type, list_of_clip_timestamps, clips_date)


    else:
        while keep_going:

            # gets clips timestamp file from user input
            if clips_file_parent:
                use_clips_parent = input(f"do you want to use the previous parent path of {clips_file_parent} for your clips file (Y) or n\n")
                use_clips_parent = y_or_n(use_clips_parent)

            if use_clips_parent:
                clips_file = input(f"please provide name of clips timestamp file you want to use in {clips_file_parent}\n")
                clips_file = build_path(clips_file_parent, clips_file)
            else:
                clips_file = input("please provide path to the clips timestamp file you want to use\n")

            #clips_file = wrap_string(clips_file)
            clips_file_parent = get_parent_folder(clips_file)

            # get clip timestamps from file
            list_of_clip_timestamps, clips_date = get_clip_timestamps(clips_file)


            # gets vod file from user input
            if vod_file_parent:
                use_vod_parent = input(f"do you want to use the previous parent path of {vod_file_parent} for your vod (Y) or n\n")
                use_vod_parent = y_or_n(use_vod_parent)
            
            if use_vod_parent:
                input_file = input(f"please provide name of the vod you want to use in {vod_file_parent}\n")
                input_file = build_path(vod_file_parent, input_file)
            else:
                input_file = input("please provide path to the vod you want to use\n")

            input_file = wrap_string(input_file)

            vod_file_parent = get_parent_folder(input_file)

            # creates clips
            create_clips(input_file, config.output_file_type, list_of_clip_timestamps, clips_date)

            # continues or exits based on user input
            keep_going = input("do you want to create more clips with different files? (Y) or N\n")
            keep_going = y_or_n(keep_going)
                
if __name__ == "__main__":

    # log exceptions
    sys.excepthook = housey_logging.log_exception

    config = config_loader.load_config()
    main()
