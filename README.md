# ✂️ Video Trimmer & Concatenator

This Python script leverages the powerful FFmpeg tool to trim specific segments from any supported video file and then combine these segments into a single, high-quality MP4 video. It's designed for efficiency, clarity in the terminal, and flexible configuration via a JSON file.

## ✨ Features

* **Universal Input Support:** Trims videos from almost any common format (MP4, MKV, AVI, MOV, WebM, etc.) supported by FFmpeg.
* **Precision Trimming:** Define exact start and end times for each segment you want to extract.
* **Automated Conversion to MP4:** Each trimmed segment is automatically re-encoded to a widely compatible MP4 format (H.264 video and AAC audio).
* **Smart Concatenation:** All processed segments are seamlessly combined into one final MP4 video.
* **Quality & Speed Control:** Fine-tune video quality (CRF), encoding speed (preset), and even output resolution directly from the configuration.
* **Clean Terminal Output:** Modern, color-coded, and emoji-enhanced output provides clear progress and feedback.
* **External Configuration:** All settings are managed in a separate `config.json` file, keeping the main script clean and easy to update.

## 🚀 Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  **FFmpeg:** This is the core engine for video processing.
    * **Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install ffmpeg`
    * **Linux (Fedora):** `sudo dnf install ffmpeg`
    * **macOS (using Homebrew):** `brew install ffmpeg`
    * **Windows:** Download a pre-built executable from [ffmpeg.org/download.html](https://ffmpeg.org/download.html). Extract it and **add the `bin` folder path to your system's PATH environment variable**. This is crucial for the script to find `ffmpeg.exe`.
2.  **Python 3:** The script is written in Python.
    * Download from [python.org](https://www.python.org/downloads/).
3.  **`colorama` Python Package:** Used for the clean, colored terminal output.
    * Install via pip: `pip install colorama`

## 📦 Installation & Setup

1.  **Download Script Files:**
    * Save the `video_trimmer.py` code into a file named `video_trimmer.py`.
    * Save the `config.json` code into a file named `config.json`.
    * Place both files in the same directory.
2.  **Install Python Dependencies:**
    ```bash
    pip install colorama
    ```
3.  **Verify FFmpeg Installation:**
    Open your terminal/command prompt and type:
    ```bash
    ffmpeg -version
    ```
    If you see version information, FFmpeg is correctly installed and in your PATH. If you get an error, review the FFmpeg installation steps for your OS.

## 🛠️ Configuration (`config.json` Guide)

The `config.json` file is where you tell the script what video to process and how. Open it with a text editor and fill in your details.

```json
{
  "video_path": "path/to/your/local/video.mkv",
  "intervals": [
    ["00:00:00", "00:00:05"],
    ["00:07:31", "00:07:34"],
    ["00:07:49", "00:07:53"]
  ],
  "concat": true,
  "output_directory": "trimmed_parts",
  "final_output_name": "final_combined_video.mp4",
  "force_reencode_concat": true,
  "video_codec_concat": "libx264",
  "audio_codec_concat": "aac",
  "crf": 23,
  "preset": "medium",
  "scale_resolution": null
}
```
Okay, that's a great idea for beginner users! I'll update the README.md to provide more comprehensive options for scale_resolution and video_codec_concat, making it clearer which choices are available and what their implications are.
## 🛠️ Configuration (`config.json` Guide)

The `config.json` file is where you tell the script what video to process and how. Open it with a text editor and fill in your details.

```json
{
  "video_path": "path/to/your/local/video.mkv",
  "intervals": [
    ["00:00:00", "00:00:05"],
    ["00:07:31", "00:07:34"],
    ["00:07:49", "00:07:53"]
  ],
  "concat": true,
  "output_directory": "trimmed_parts",
  "final_output_name": "final_combined_video.mp4",
  "force_reencode_concat": true,
  "video_codec_concat": "libx264",
  "audio_codec_concat": "aac",
  "crf": 23,
  "preset": "medium",
  "scale_resolution": null
}
```

Parameter Explanations:
 * "video_path" (Required)
   * Type: string
   * Description: The full path to your input video file. This can be an MP4, MKV, AVI, MOV, WebM, etc.
   * Examples:
     * Windows: "C:/Users/YourUser/Videos/my_awesome_video.mkv" or "C:\\Users\\YourUser\\Videos\\my_awesome_video.mkv"
     * macOS/Linux: "/Users/YourUser/Videos/my_awesome_video.mp4"
     * Relative path (if video is in the same directory as the script): "my_awesome_video.mov"
 * "intervals" (Required)
   * Type: array of arrays of strings
   * Description: A list of [start_time, end_time] pairs, defining each segment you want to extract.
   * Time Format: HH:MM:SS (Hours:Minutes:Seconds). You can omit leading zeros (e.g., 00:00:05 can be 5 or 0:5).
   * Example: [["00:00:00", "00:00:05"], ["00:01:30", "00:02:00"]] would extract the first 5 seconds and then the segment from 1 minute 30 seconds to 2 minutes.
 * "concat" (Required)
   * Type: boolean
   * Description: If true, all trimmed segments will be combined into one final_output_name video. If false, individual trimmed files will be left in the output_directory and no final concatenation will occur.
 * "output_directory" (Required)
   * Type: string
   * Description: The name of the folder where trimmed segments (and the final combined video, if concat is true) will be saved. This folder will be created if it doesn't exist.
   * Example: "trimmed_parts"
 * "final_output_name" (Required)
   * Type: string
   * Description: The filename for the final combined video (if concat is true). It must end with .mp4.
   * Example: "my_awesome_compilation.mp4"
 * "force_reencode_concat" (Recommended: true)
   * Type: boolean
   * Description: Keep this as true for universal compatibility with MP4. When true, each trimmed segment will be re-encoded to H.264/AAC during the trimming step to ensure it's compatible for the final MP4 output. If false, it would attempt a direct stream copy, which often fails if source codecs are not MP4-compatible.
 * "video_codec_concat" (Recommended: "libx264")
   * Type: string
   * Description: The video codec to use for the re-encoding process.
   * Options:
     * "libx264": (Recommended for beginners) This is the standard H.264 encoder. It offers excellent compression and is widely compatible across almost all devices and platforms (TVs, phones, web browsers). Good balance of quality and file size.
     * "libx265": Uses H.265 (HEVC) encoding. Offers significantly better compression than H.264 (meaning smaller files for similar quality), but requires more processing power to encode and decode. Compatibility is good on newer devices but might be an issue on older ones.
     * "vp9": A royalty-free codec often used in WebM containers (though can be in MP4). Good compression but less universally supported in MP4 than H.264/H.265.
     * h264_nvenc, hevc_nvenc: (NVIDIA GPU hardware acceleration). Advanced option. Requires a compatible NVIDIA GPU. Significantly faster encoding speeds, but usually produces larger files or slightly lower quality compared to libx264 (CPU-based) at the same settings.
     * h264_qsv, hevc_qsv: (Intel Quick Sync Video hardware acceleration). Advanced option. Requires a compatible Intel processor with Quick Sync. Similar benefits and trade-offs to NVENC.
     * h264_amf, hevc_amf: (AMD GPU hardware acceleration). Advanced option. Requires a compatible AMD GPU. Similar benefits and trade-offs.
   * Choosing: For most users and maximum compatibility with good results, stick with "libx264". If you have newer devices and want smaller files, try "libx265".
 * "audio_codec_concat" (Recommended: "aac")
   * Type: string
   * Description: The audio codec to use for the re-encoding process. aac is highly recommended for broad MP4 compatibility.
 * "crf" (Optional: 23 is a good start)
   * Type: integer (0-51)
   * Description: Constant Rate Factor for video quality control.
     * Lower value = Higher quality, larger file size.
     * Higher value = Lower quality, smaller file size.
     * 18 is often considered "visually lossless."
     * 23 is the default and a good balance.
     * To reduce file size, try 26, 28, or 30.
     * If not set, FFmpeg's default for libx264 is 23.
 * "preset" (Optional: "medium" is a good start)
   * Type: string
   * Description: Controls the speed vs. compression efficiency for video encoding.
     * Faster presets = Quicker encoding, larger file size.
     * Slower presets = Longer encoding, smaller file size.
     * Options (fastest to slowest): ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo.
     * medium is a good balance. If encoding is too slow, try fast or veryfast. If you want the smallest possible file and don't mind waiting, try slow or slower.
     * If not set, FFmpeg's default for libx264 is medium.
 * "scale_resolution" (Optional: null by default)
   * Type: string or null
   * Description: Scales the output video resolution.
     * Set to null to keep the original resolution.
     * Use WIDTH:-1 or -1:HEIGHT to specify a dimension while maintaining aspect ratio.
     * Recommendation: Scaling down (e.g., 4K to 1080p) saves significant file size. Scaling up (e.g., 720p to 1080p) will increase file size without adding actual detail/quality.
     * Common Options:
       * "854:-1" or "-1:480": For 480p (SD - Standard Definition)
       * "1280:-1" or "-1:720": For 720p (HD - High Definition)
       * "1920:-1" or "-1:1080": (Recommended for Full HD) For 1080p (Full HD - High Definition)
       * "2560:-1" or "-1:1440": For 1440p (2K / QHD - Quad High Definition)
       * "3840:-1" or "-1:2160": For 2160p (4K / UHD - Ultra High Definition)
       * "4096:-1" or "-1:2160": For 2160p (DCI 4K - Cinema 4K)
<!-- end list -->



🚀 Usage
 * Configure config.json: Edit the config.json file with your video_path, intervals, and other desired settings as detailed above.
 * Open Your Terminal/Command Prompt: Navigate to the directory where you saved video_trimmer.py and config.json.
 * Run the Script:
   python video_trimmer.py

The script will provide clear, color-coded feedback on its progress, including trimming each part, the final concatenation, and cleanup.
💡 Workflow Explanation
This script employs an efficient two-stage process for trimming and combining videos:
 * Trim & Convert Each Part:
   * The script reads your config.json and iterates through each interval.
   * For each interval, it executes an FFmpeg command to extract that specific segment from your input video.
   * Crucially, during this extraction, it re-encodes the segment to H.264 video and AAC audio (using your specified crf, preset, and scale_resolution). This ensures that every individual trimmed part (e.g., trimmed_parts/part-00.mp4, trimmed_parts/part-01.mp4) is immediately in a highly compatible MP4 format.
   * This step can be time-consuming, as it involves re-encoding.
 * Lossless Concatenation:
   * Once all segments have been trimmed and converted to MP4, the script collects the paths of all these temporary MP4 files.
   * It then executes a single FFmpeg command using the concat demuxer. Because all the individual parts are already in a compatible MP4 format, this final step is extremely fast and lossless (-c copy). FFmpeg simply stitches the already-compatible streams together without any further re-encoding.
   * Finally, the script cleans up the individual trimmed parts, leaving only your final combined MP4 video.
This workflow guarantees a universally compatible MP4 output and keeps the final merge very fast.
⚠️ Troubleshooting
 * FFmpeg executable not found error:
   * Solution: Ensure FFmpeg is installed and its executable path is added to your system's PATH environment variable. Restart your terminal after making PATH changes.
 * Error decoding JSON from 'config.json':
   * Solution: Your config.json file has a syntax error. Double-check for missing commas, unclosed brackets [] or braces {}, or incorrect quotes. Use an online JSON validator if needed.
 * Input video 'path/to/your/video.mp4' not found:
   * Solution: Verify that the video_path in your config.json is absolutely correct and includes the full path to your video file.
 * "Video quality is low" or "File size is too big":
   * Solution: Adjust the crf and preset values in your config.json.
     * For higher quality/larger size: Lower crf (e.g., 18-22), use slow or slower preset.
     * For lower quality/smaller size: Increase crf (e.g., 26-30), use fast or ultrafast preset.
 * Process hangs or consumes too much memory/CPU:
   * Solution: You might be trying to process a very large number of intervals or very high-resolution video on limited hardware. Try breaking it down into smaller batches or adjust your preset to fast or veryfast to reduce CPU usage at the cost of file size.
📄 License
This project is open-source and available under the MIT License.
🙏 Acknowledgements
 * FFmpeg: The powerful open-source multimedia framework that does all the heavy lifting.
 * Colorama: For making the terminal output look awesome.

