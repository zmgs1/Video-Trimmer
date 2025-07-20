import subprocess
import os
import shutil
import json
from colorama import init, Fore, Style # Import colorama for styling

# Initialize colorama (needed for Windows to work correctly)
init(autoreset=True)

# Define color shortcuts and emojis for clean terminal output
INFO = Fore.CYAN + Style.BRIGHT + "ⓘ "
SUCCESS = Fore.GREEN + Style.BRIGHT + "✔ "
WARNING = Fore.YELLOW + Style.BRIGHT + "▲ "
ERROR = Fore.RED + Style.BRIGHT + "✖ "
SECTION = Fore.MAGENTA + Style.BRIGHT + "─" * 5 + " "
SUBSECTION = Fore.BLUE + "› "

def run_ffmpeg_command(command, suppress_output=True):
    """Executes an FFmpeg command and handles errors, with controlled output."""
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            bufsize=1 # Line-buffered output
        )

        if suppress_output:
            # Consume output without printing to terminal to prevent buffering issues
            stdout, stderr = process.communicate()
        else:
            # Print output in real-time if not suppressed (for verbose debugging)
            for line in process.stdout:
                print(f"{INFO}{Fore.WHITE}{line.strip()}")
            stdout, stderr = process.communicate() # Collect any remaining output

        if process.returncode != 0:
            print(f"{ERROR}FFmpeg command failed with exit code {process.returncode}")
            print(f"{ERROR}STDOUT:\n{stdout}")
            print(f"{ERROR}STDERR:\n{stderr}")
            raise subprocess.CalledProcessError(process.returncode, command, stdout=stdout, stderr=stderr)
        else:
            if not suppress_output: # Only print success if output was not suppressed
                print(f"{SUCCESS}FFmpeg command completed.")
            return stdout, stderr

    except subprocess.CalledProcessError as e:
        print(f"{ERROR}Failed to execute FFmpeg command: {e}")
        raise
    except FileNotFoundError:
        print(f"{ERROR}FFmpeg executable not found. Please ensure FFmpeg is installed and in your system's PATH.")
        raise
    except Exception as e:
        print(f"{ERROR}An unexpected error occurred during FFmpeg execution: {e}")
        raise

def trim_video(input_path, output_dir, start_time, end_time, filename_prefix, index,
               video_codec="libx264", audio_codec="aac", crf=None, preset=None, scale_resolution=None):
    """
    Trims a video segment and immediately converts it to MP4 format with specified codecs.
    """
    # Output will always be MP4 for intermediate files as per the workflow
    output_filename = f"{filename_prefix}-{str(index).zfill(2)}.mp4"
    output_path = os.path.join(output_dir, output_filename)

    codec_options = f"-c:v {video_codec} -c:a {audio_codec}"

    if crf is not None:
        codec_options += f" -crf {crf}"
    if preset is not None:
        codec_options += f" -preset {preset}"
    
    # Add scale filter if scale_resolution is provided
    scale_filter = ""
    if scale_resolution:
        scale_filter = f' -vf "scale={scale_resolution}"'
        print(f"{SUBSECTION}  Scaling to: {Fore.WHITE}{scale_resolution}{Style.RESET_ALL}")

    command = (
        f'ffmpeg -ss {start_time} -i "{input_path}" -to {end_time} '
        f'{codec_options}{scale_filter} -loglevel quiet -y "{output_path}"' # -loglevel quiet suppresses FFmpeg's default output, -y overwrites
    )
    print(f"{SUBSECTION}Trimming & Converting: {Fore.WHITE}{input_path} [{start_time} - {end_time}]{Style.RESET_ALL}") # Corrected 'to_time' to 'end_time'
    print(f"{SUBSECTION}  Outputting to: {Fore.WHITE}{output_path}{Style.RESET_ALL}")
    run_ffmpeg_command(command)
    print(f"{SUCCESS}Part {str(index).zfill(2)} processed successfully as MP4!")
    return output_path

def concatenate_videos(input_files, output_path, temp_list_file="concat_list.txt"):
    """
    Concatenates multiple pre-encoded MP4 video files using FFmpeg's concat demuxer.
    This process is now fast and lossless as files are already compatible.
    """
    with open(temp_list_file, 'w', encoding='utf-8') as f:
        for file_path in input_files:
            formatted_path = file_path.replace("\\", "/") # Ensure forward slashes for FFmpeg list file
            f.write(f"file '{formatted_path}'\n")

    # Since individual parts are already MP4-compatible, we just copy them.
    codec_options = "-c copy"

    print(f"{SUBSECTION}Concatenating pre-encoded MP4 parts. This will be fast.{Style.RESET_ALL}")

    command = (
        f'ffmpeg -f concat -safe 0 -i "{temp_list_file}" '
        f'{codec_options} -loglevel quiet -y "{output_path}"' # -loglevel quiet, -y overwrites
    )
    print(f"{SUBSECTION}Combining {len(input_files)} parts into: {Fore.WHITE}{output_path}{Style.RESET_ALL}")
    run_ffmpeg_command(command)
    os.remove(temp_list_file) # Clean up the temporary list file
    print(f"{SUCCESS}Final concatenation finished successfully!")

def main():
    config_file = 'config.json'
    print(f"{SECTION}Starting Video Processing Script{Style.RESET_ALL}")

    # --- Load Configuration ---
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

    # --- Pre-checks ---
    print(f"{INFO}Performing pre-flight checks...{Style.RESET_ALL}")
    if not os.path.exists(data['video_path']):
        print(f"{ERROR}Input video '{data['video_path']}' not found. Please update 'video_path' in '{config_file}'.")
        return
    print(f"{SUCCESS}Input video found: {Fore.WHITE}{data['video_path']}{Style.RESET_ALL}")

    os.makedirs(data['output_directory'], exist_ok=True)
    print(f"{SUCCESS}Output directory ensured: {Fore.WHITE}{data['output_directory']}{Style.RESET_ALL}")

    trimmed_part_paths = []

    try:
        # --- Trimming and Converting Intervals to MP4 ---
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
                # Pass re-encoding parameters to trim_video
                video_codec=data.get('video_codec_concat', 'libx264'),
                audio_codec=data.get('audio_codec_concat', 'aac'),
                crf=data.get('crf'),
                preset=data.get('preset'),
                scale_resolution=data.get('scale_resolution')
            )
            trimmed_part_paths.append(trimmed_file_path)

        if data['concat']:
            # --- Concatenation (Lossless Remux) ---
            final_output_path = os.path.join(data['output_directory'], data['final_output_name'])
            print(f"\n{SECTION}Starting Final Video Concatenation (Fast Remux){Style.RESET_ALL}")
            concatenate_videos(
                trimmed_part_paths,
                final_output_path
                # No need to pass re-encoding parameters here, as parts are already MP4
            )

            # --- Cleanup ---
            print(f"\n{SECTION}Cleaning Up Temporary Files{Style.RESET_ALL}")
            for part_path in trimmed_part_paths:
                if os.path.exists(part_path):
                    print(f"{INFO}Removing temporary file: {Fore.WHITE}{os.path.basename(part_path)}{Style.RESET_ALL}")
                    os.remove(part_path)
            print(f"{SUCCESS}Temporary files cleaned up.{Style.RESET_ALL}")

        print(f"\n{SUCCESS}All operations completed successfully! Final video saved to: {Fore.WHITE}{final_output_path if data['concat'] else 'individual trimmed MP4 parts'}{Style.RESET_ALL}")

    except Exception as e:
        print(f"\n{ERROR}An unexpected error occurred during processing: {e}")
        import traceback
        traceback.print_exc()
        print(f"{WARNING}Temporary trimmed files might still be in '{data['output_directory']}'. Please check manually.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
