# ffmpeg Command Recipes

Copy-paste recipes for common video/audio processing tasks.

## Format Conversion

### Container Change (No Re-encode)
```bash
# MOV to MP4
ffmpeg -i input.mov -c copy output.mp4

# MKV to MP4
ffmpeg -i input.mkv -c copy output.mp4

# MP4 to MKV (keeps all tracks)
ffmpeg -i input.mp4 -c copy output.mkv
```

### Full Re-encode

**Hardware (fast):**
```bash
ffmpeg -hwaccel videotoolbox -i input.mov \
  -c:v hevc_videotoolbox -q:v 75 -tag:v hvc1 \
  -c:a aac -b:a 192k \
  output.mp4
```

**Software (better compression):**
```bash
ffmpeg -i input.mov \
  -c:v libx264 -crf 23 -preset medium \
  -c:a aac -b:a 192k \
  output.mp4
```

## Compression

### Reduce File Size (Hardware)
```bash
# Moderate compression
ffmpeg -hwaccel videotoolbox -i input.mp4 \
  -c:v hevc_videotoolbox -q:v 70 -tag:v hvc1 \
  -c:a aac -b:a 128k \
  compressed.mp4

# Aggressive compression
ffmpeg -hwaccel videotoolbox -i input.mp4 \
  -c:v hevc_videotoolbox -q:v 55 -tag:v hvc1 \
  -c:a aac -b:a 96k \
  small.mp4
```

### Reduce File Size (Software - Best Compression)
```bash
# High quality, smaller file
ffmpeg -i input.mp4 \
  -c:v libx265 -crf 28 -preset slow \
  -c:a aac -b:a 128k \
  compressed.mp4

# Maximum compression
ffmpeg -i input.mp4 \
  -c:v libx265 -crf 32 -preset slower \
  -c:a aac -b:a 96k \
  tiny.mp4
```

### Target File Size
```bash
# Calculate bitrate: target_size_MB * 8192 / duration_seconds = bitrate_kbps
# Example: 100MB file, 600 second video = ~1365 kbps

ffmpeg -i input.mp4 \
  -c:v libx264 -b:v 1200k -pass 1 -f null /dev/null && \
ffmpeg -i input.mp4 \
  -c:v libx264 -b:v 1200k -pass 2 \
  -c:a aac -b:a 128k \
  output.mp4
```

## Audio Operations

### Extract Audio (Keep Original Format)
```bash
ffmpeg -i video.mp4 -vn -c:a copy audio.m4a
```

### Extract to MP3
```bash
# High quality MP3
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 0 audio.mp3

# Standard quality
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3

# Fixed bitrate
ffmpeg -i video.mp4 -vn -acodec libmp3lame -b:a 320k audio.mp3
```

### Extract to AAC
```bash
ffmpeg -i video.mp4 -vn -c:a aac -b:a 256k audio.m4a
```

### Extract to FLAC (Lossless)
```bash
ffmpeg -i video.mp4 -vn -c:a flac audio.flac
```

### Replace Audio Track
```bash
ffmpeg -i video.mp4 -i new_audio.mp3 \
  -c:v copy -c:a aac \
  -map 0:v:0 -map 1:a:0 \
  output.mp4
```

### Remove Audio
```bash
ffmpeg -i input.mp4 -c:v copy -an output.mp4
```

### Normalize Audio Volume
```bash
# Analyze
ffmpeg -i input.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null -

# Apply (use values from analysis)
ffmpeg -i input.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 output.mp4
```

## Trimming & Cutting

### Trim by Duration
```bash
# Start at 1 minute, take 30 seconds (fast, stream copy)
ffmpeg -i input.mp4 -ss 00:01:00 -t 00:00:30 -c copy clip.mp4

# Start at 1 minute, take 30 seconds (accurate, re-encode)
ffmpeg -i input.mp4 -ss 00:01:00 -t 00:00:30 -c:v libx264 -c:a aac clip.mp4
```

### Trim by End Time
```bash
# From 1:00 to 1:30
ffmpeg -i input.mp4 -ss 00:01:00 -to 00:01:30 -c copy clip.mp4
```

### Remove Beginning
```bash
# Skip first 10 seconds
ffmpeg -i input.mp4 -ss 00:00:10 -c copy trimmed.mp4
```

### Remove End
```bash
# Keep first 2 minutes
ffmpeg -i input.mp4 -t 00:02:00 -c copy trimmed.mp4
```

### Split into Multiple Parts
```bash
# Part 1: 0:00 - 5:00
ffmpeg -i input.mp4 -ss 00:00:00 -t 00:05:00 -c copy part1.mp4

# Part 2: 5:00 - 10:00
ffmpeg -i input.mp4 -ss 00:05:00 -t 00:05:00 -c copy part2.mp4
```

## Merging & Concatenation

### Merge Video + Audio
```bash
# Video and audio same duration
ffmpeg -i video.mp4 -i audio.m4a -c copy merged.mp4

# If different durations, use shortest
ffmpeg -i video.mp4 -i audio.m4a -c copy -shortest merged.mp4
```

### Concatenate Multiple Videos (Same Codec)
```bash
# Create list.txt:
echo "file 'video1.mp4'" > list.txt
echo "file 'video2.mp4'" >> list.txt
echo "file 'video3.mp4'" >> list.txt

# Concatenate
ffmpeg -f concat -safe 0 -i list.txt -c copy combined.mp4
```

### Concatenate (Different Codecs - Re-encode)
```bash
ffmpeg -f concat -safe 0 -i list.txt \
  -c:v libx264 -crf 23 \
  -c:a aac -b:a 192k \
  combined.mp4
```

## Scaling & Resolution

### Scale to Specific Resolution
```bash
# 1920x1080
ffmpeg -i input.mp4 -vf "scale=1920:1080" output.mp4

# 1280x720
ffmpeg -i input.mp4 -vf "scale=1280:720" output.mp4
```

### Scale Maintaining Aspect Ratio
```bash
# Scale to 720p height
ffmpeg -i input.mp4 -vf "scale=-1:720" output.mp4

# Scale to 1080p height
ffmpeg -i input.mp4 -vf "scale=-1:1080" output.mp4

# Scale to 1920 width
ffmpeg -i input.mp4 -vf "scale=1920:-1" output.mp4
```

### Scale with Padding (Letterbox)
```bash
# Scale to fit 1920x1080 with black bars
ffmpeg -i input.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" output.mp4
```

### Change Frame Rate
```bash
# Convert to 30fps
ffmpeg -i input.mp4 -r 30 output.mp4

# Convert to 24fps
ffmpeg -i input.mp4 -r 24 output.mp4
```

## Subtitles

### Burn-in Subtitles (Hardcode)
```bash
# SRT file
ffmpeg -i input.mp4 -vf "subtitles=subs.srt" output.mp4

# ASS file (with styling)
ffmpeg -i input.mp4 -vf "ass=subs.ass" output.mp4

# With font settings
ffmpeg -i input.mp4 -vf "subtitles=subs.srt:force_style='FontSize=24,FontName=Arial'" output.mp4
```

### Add Subtitles as Track (Soft Subs)
```bash
# MP4 (limited subtitle support)
ffmpeg -i input.mp4 -i subs.srt -c copy -c:s mov_text output.mp4

# MKV (full subtitle support)
ffmpeg -i input.mp4 -i subs.srt -c copy -c:s srt output.mkv
```

### Extract Subtitles
```bash
# First subtitle track
ffmpeg -i input.mkv -map 0:s:0 output.srt

# All subtitle tracks
ffmpeg -i input.mkv -map 0:s subs.srt

# Specific track by index
ffmpeg -i input.mkv -map 0:s:1 english.srt
```

### Convert Subtitle Format
```bash
# VTT to SRT
ffmpeg -i input.vtt output.srt

# SRT to ASS
ffmpeg -i input.srt output.ass
```

## Image & GIF Operations

### Extract Single Frame
```bash
# At specific timestamp
ffmpeg -i input.mp4 -ss 00:00:05 -frames:v 1 thumbnail.png

# Best quality JPEG
ffmpeg -i input.mp4 -ss 00:00:05 -frames:v 1 -q:v 2 thumbnail.jpg
```

### Extract Multiple Frames
```bash
# Every frame
ffmpeg -i input.mp4 frames/frame_%04d.png

# One per second
ffmpeg -i input.mp4 -vf fps=1 frames/frame_%04d.png

# Every 10 seconds
ffmpeg -i input.mp4 -vf fps=1/10 frames/frame_%04d.png
```

### Create Video from Images
```bash
# From numbered images
ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4

# From glob pattern
ffmpeg -framerate 30 -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p output.mp4
```

### Create GIF
```bash
# Simple GIF
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1" output.gif

# High quality GIF (with palette)
ffmpeg -i input.mp4 -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" output.gif

# From specific section
ffmpeg -i input.mp4 -ss 00:00:05 -t 00:00:03 -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" output.gif
```

## Speed Manipulation

### Speed Up Video
```bash
# 2x speed
ffmpeg -i input.mp4 -filter:v "setpts=0.5*PTS" -filter:a "atempo=2.0" fast.mp4

# 4x speed (audio needs chaining)
ffmpeg -i input.mp4 -filter:v "setpts=0.25*PTS" -filter:a "atempo=2.0,atempo=2.0" fast.mp4
```

### Slow Down Video
```bash
# 0.5x speed (slow motion)
ffmpeg -i input.mp4 -filter:v "setpts=2.0*PTS" -filter:a "atempo=0.5" slow.mp4

# 0.25x speed
ffmpeg -i input.mp4 -filter:v "setpts=4.0*PTS" -filter:a "atempo=0.5,atempo=0.5" slow.mp4
```

### Speed Up Without Audio
```bash
ffmpeg -i input.mp4 -filter:v "setpts=0.5*PTS" -an fast_noaudio.mp4
```

## Batch Processing

### Convert All Files in Directory
```bash
# MOV to MP4 (hardware)
for f in *.mov; do
  ffmpeg -hwaccel videotoolbox -i "$f" -c:v hevc_videotoolbox -q:v 75 -tag:v hvc1 -c:a aac "${f%.mov}.mp4"
done

# AVI to MP4 (software)
for f in *.avi; do
  ffmpeg -i "$f" -c:v libx264 -crf 23 -c:a aac "${f%.avi}.mp4"
done
```

### Batch Compress
```bash
for f in *.mp4; do
  ffmpeg -hwaccel videotoolbox -i "$f" -c:v hevc_videotoolbox -q:v 65 -tag:v hvc1 -c:a aac -b:a 128k "compressed/${f}"
done
```

### Batch Extract Audio
```bash
for f in *.mp4; do
  ffmpeg -i "$f" -vn -c:a copy "${f%.mp4}.m4a"
done
```

### Parallel Processing
```bash
# Using GNU parallel
find . -name "*.mov" | parallel -j 4 ffmpeg -i {} -c:v libx264 -crf 23 {.}.mp4
```

## Metadata Operations

### View Metadata
```bash
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

### Strip All Metadata
```bash
ffmpeg -i input.mp4 -c copy -map_metadata -1 output.mp4
```

### Add Metadata
```bash
ffmpeg -i input.mp4 -c copy \
  -metadata title="My Video" \
  -metadata artist="Author Name" \
  -metadata year="2024" \
  output.mp4
```

### Copy Metadata from Another File
```bash
ffmpeg -i input.mp4 -i metadata_source.mp4 \
  -c copy -map 0 -map_metadata 1 \
  output.mp4
```

## Screen Recording Post-Processing

### Compress Screen Recording
```bash
# QuickTime recordings are huge, compress:
ffmpeg -hwaccel videotoolbox -i screen_recording.mov \
  -c:v hevc_videotoolbox -q:v 70 -tag:v hvc1 \
  -c:a aac -b:a 128k \
  compressed.mp4
```

### Remove Silence/Dead Air
```bash
# Detect silence
ffmpeg -i input.mp4 -af silencedetect=n=-50dB:d=1 -f null -

# Then trim manually based on timestamps
```

### Add Fade In/Out
```bash
# Fade in first 2 seconds, fade out last 2 seconds
ffmpeg -i input.mp4 \
  -vf "fade=t=in:st=0:d=2,fade=t=out:st=58:d=2" \
  -af "afade=t=in:st=0:d=2,afade=t=out:st=58:d=2" \
  output.mp4
# Adjust st (start time) based on video duration
```
