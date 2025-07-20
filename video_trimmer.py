import subprocess
import os
import shutil
import json
import re
from colorama import init, Fore, Style
import sys
import time # Import time for a small delay in spinner updates

# Initialize colorama
init(autoreset=True)

# Define color shortcuts and emojis for clean terminal output
INFO = Fore.CYAN + Style.BRIGHT + "ⓘ "
SUCCESS = Fore.GREEN + Style.BRIGHT + "✔ "
WARNING = Fore.YELLOW + Style.BRIGHT + "▲ "
ERROR = Fore.RED + Style.BRIGHT + "✖ "
SECTION = Fore.MAGENTA + Style.BRIGHT + "─" * 5 + " "
SUBSECTION = Fore.BLUE + "› "
ANIMATION_COLOR = Fore.YELLOW # Color for the spinner animation

# --- Utility Function to Convert Time (kept, though not used for spinner directly) ---
def parse_time_to_seconds(time_str):
    """Converts HH:MM:SS or SS format to total seconds."""
    parts = list(map(float, time_str.split(':')))
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2: # MM:SS
        return parts[0] * 60 + parts[1]
    elif len(parts) == 1: # SS
        return parts[0]
    return 0

# --- MODIFIED run_ffmpeg_command for spinner animation ---
def run_ffmpeg_command(command): # Removed total_duration_seconds as it's not needed for spinner
    """
    Executes an FFmpeg command and handles errors, with a waiting animation.
    FFmpeg's verbose output is suppressed unless an error occurs.
    """
    process = None
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, # Still capture stderr to know when it's done
            text=True,
            encoding='utf-8',
            bufsize=1
        )

        spinner = ['|', '/', '-', '\\']
        spinner_idx = 0
        animation_active = True
        
        # Read stderr non-blockingly to allow spinner updates
        while animation_active and process.poll() is None: # While process is running
            # Read a line from stderr, but don't block indefinitely
            line = process.stderr.readline() 
            if line:
                # We consume FFmpeg's output but don't print it to keep clean terminal
                # You can add debug logging here if you need to see raw FFmpeg output
                pass 
            
            # Update spinner
            sys.stdout.write(f"\r{ANIMATION_COLOR}Processing {spinner[spinner_idx]} {Style.RESET_ALL}")
            sys.stdout.flush()
            spinner_idx = (spinner_idx + 1) % len(spinner)
            time.sleep(0.1) # Small delay for animation speed

        # Ensure a final newline after the animation stops
        sys.stdout.write("\n")
        sys.stdout.flush()

        # Collect any remaining stdout/stderr for error reporting
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"{ERROR}FFmpeg command failed with exit code {process.returncode}")
            if stdout: print(f"{ERROR}STDOUT:\n{stdout}")
            if stderr: print(f"{ERROR}STDERR:\n{stderr}")
            raise subprocess.CalledProcessError(process.returncode, command, stdout=stdout, stderr=stderr)

    except subprocess.CalledProcessError as e:
        print(f"{ERROR}Failed to execute FFmpeg command: {e}")
        raise
    except FileNotFoundError:
        print(f"{ERROR}FFmpeg executable not found. Please ensure FFmpeg is installed and in your system's PATH.")
        raise
    except Exception as e:
        print(f"{ERROR}An unexpected error occurred during FFmpeg execution: {e}")
        if process:
            try:
                process.kill()
            except OSError:
                pass
        raise

# --- MODIFIED trim_video: REMOVED duration calculation and argument ---
def trim_video(input_path, output_dir, start_time, end_time, filename_prefix, index,
               video_codec="libx264", audio_codec="aac", crf=None, preset=None, scale_resolution=None):
    """
    Trims a video segment and immediately converts it to MP4 format with specified codecs.
    Shows a waiting animation.
    """
    output_filename = f"{filename_prefix}-{str(index).zfill(2)}.mp4"
    output_path = os.path.join(output_dir, output_filename)

    codec_options = f"-c:v {video_codec} -c:a {audio_codec}"
    if crf is not None:
        codec_options += f" -crf {crf}"
    if preset is not None:
        codec_options += f" -preset {preset}"
    
    scale_filter = ""
    if scale_resolution:
        scale_filter = f' -vf "scale={scale_resolution}"'
        print(f"{SUBSECTION}  Scaling to: {Fore.WHITE}{scale_resolution}{Style.RESET_ALL}")

    # Validation: Check for valid interval (start < end)
    start_seconds = parse_time_to_seconds(start_time)
    end_seconds = parse_time_to_seconds(end_time)
    if start_seconds >= end_seconds:
        print(f"{WARNING}Invalid interval: Start time {start_time} is not before end time {end_time}. Skipping part {index+1}.{Style.RESET_ALL}")
        return None

    # IMPORTANT: Removed -loglevel quiet from here so FFmpeg outputs *some* stderr for process completion detection
    command = (
        f'ffmpeg -ss {start_time} -i "{input_path}" -to {end_time} '
        f'{codec_options}{scale_filter} -y "{output_path}"'
    )
    print(f"{SUBSECTION}Trimming & Converting: {Fore.WHITE}{input_path} [{start_time} - {end_time}]{Style.RESET_ALL}")
    print(f"{SUBSECTION}  Outputting to: {Fore.WHITE}{output_path}{Style.RESET_ALL}")
    
    # Call run_ffmpeg_command without duration
    run_ffmpeg_command(command)
    
    print(f"{SUCCESS}Part {str(index).zfill(2)} processed successfully as MP4!")
    return output_path

# --- concatenate_videos (no change needed here) ---
def concatenate_videos(input_files, output_path, temp_list_file="concat_list.txt"):
    """
    Concatenates multiple pre-encoded MP4 video files using FFmpeg's concat demuxer.
    This process is now fast and lossless as files are already compatible.
    """
    with open(temp_list_file, 'w', encoding='utf-8') as f:
        for file_path in input_files:
            formatted_path = file_path.replace("\\", "/")
            f.write(f"file '{formatted_path}'\n")

    codec_options = "-c copy"

    print(f"{SUBSECTION}Concatenating pre-encoded MP4 parts. This will be fast.{Style.RESET_ALL}")

    command = (
        f'ffmpeg -f concat -safe 0 -i "{temp_list_file}" '
        f'{codec_options} -loglevel quiet -y "{output_path}"' # Still use -loglevel quiet here for clean concat
    )
    print(f"{SUBSECTION}Combining {len(input_files)} parts into: {Fore.WHITE}{output_path}{Style.RESET_ALL}")
    # No animation for concat as it's typically very fast
    run_ffmpeg_command(command) # Call without duration
    os.remove(temp_list_file)
    print(f"{SUCCESS}Final concatenation finished successfully!")

# --- main function (no changes needed) ---
def main():
    config_file = 'config.json'
    print(f"{SECTION}Starting Video Processing Script{Style.RESET_ALL}")

    print(f"{INFO}Loading configuration from '{config_file}'...")
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"{SUCCESS}Configuration loaded successfully.{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{ERROR}Configuration file '{config_file}' not found.")
        print(f"{ERROR}Please create 'config.json' in the same directory as the script with your settings.")
        return
    except json.JSONDecodeError as e:
        print(f"{ERROR}Error decoding JSON from '{config_file}': {e}")
        print(f"{ERROR}Please check the syntax of your config.json file.")
        return

    print(f"{INFO}Performing pre-flight checks...{Style.RESET_ALL}")
    if not os.path.exists(data['video_path']):
        print(f"{ERROR}Input video '{data['video_path']}' not found. Please update 'video_path' in '{config_file}'.")
        return
    print(f"{SUCCESS}Input video found: {Fore.WHITE}{data['video_path']}{Style.RESET_ALL}")

    os.makedirs(data['output_directory'], exist_ok=True)
    print(f"{SUCCESS}Output directory ensured: {Fore.WHITE}{data['output_directory']}{Style.RESET_ALL}")

    trimmed_part_paths = []

    try:
        print(f"\n{SECTION}Trimming and Converting Video Intervals to MP4 ({len(data['intervals'])} parts){Style.RESET_ALL}")
        for i, (from_time, to_time) in enumerate(data['intervals']):
            print(f"\n{INFO}Processing part {i+1}/{len(data['intervals'])}...")
            trimmed_file_path = trim_video(
                data['video_path'],
                data['output_directory'],
                from_time,
                to_time,
                "part",
                i,
                video_codec=data.get('video_codec_concat', 'libx264'),
                audio_codec=data.get('audio_codec_concat', 'aac'),
                crf=data.get('crf'),
                preset=data.get('preset'),
                scale_resolution=data.get('scale_resolution')
            )
            if trimmed_file_path:
                trimmed_part_paths.append(trimmed_file_path)

        if data['concat'] and trimmed_part_paths:
            final_output_path = os.path.join(data['output_directory'], data['final_output_name'])
            print(f"\n{SECTION}Starting Final Video Concatenation (Fast Remux){Style.RESET_ALL}")
            concatenate_videos(
                trimmed_part_paths,
                final_output_path
            )
        elif data['concat'] and not trimmed_part_paths:
            print(f"{WARNING}No parts were successfully trimmed. Skipping concatenation.{Style.RESET_ALL}")

        print(f"\n{SECTION}Cleaning Up Temporary Files{Style.RESET_ALL}")
        for part_path in trimmed_part_paths:
            if os.path.exists(part_path):
                print(f"{INFO}Removing temporary file: {Fore.WHITE}{os.path.basename(part_path)}{Style.RESET_ALL}")
                os.remove(part_path)
        print(f"{SUCCESS}Temporary files cleaned up.{Style.RESET_ALL}")


        print(f"\n{SUCCESS}All operations completed successfully! Final video saved to: {Fore.WHITE}{final_output_path if data.get('concat') and trimmed_part_paths else 'individual trimmed MP4 parts'}{Style.RESET_ALL}")

    except Exception as e:
        print(f"\n{ERROR}An unexpected error occurred during processing: {e}")
        import traceback
        traceback.print_exc()
        print(f"{WARNING}Temporary trimmed files might still be in '{data['output_directory']}'. Please check manually.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
