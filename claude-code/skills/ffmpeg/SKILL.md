---
name: ffmpeg
description: This skill should be used for video and audio processing including format conversion, compression, trimming, merging, and hardware-accelerated encoding. Covers ffmpeg commands for MP4/MKV/AVI/MOV conversion, H.264/H.265/HEVC encoding, audio extraction, VideoToolbox hardware acceleration on Apple Silicon M3, subtitle handling, batch processing, and post-download video manipulation workflows.
---

# ffmpeg Video/Audio Processing Skill

Comprehensive video and audio processing using ffmpeg with hardware acceleration on Apple Silicon.

## Installation Check

```bash
# Verify ffmpeg installed
ffmpeg -version

# Check hardware acceleration available
ffmpeg -hwaccels
# Should show: videotoolbox

# Install if missing
brew install ffmpeg
```

## When to Use ffmpeg

**USE ffmpeg for:**
- Video format conversion (MP4 ↔ MKV ↔ AVI ↔ MOV)
- Video compression and quality reduction
- Audio extraction from video files
- Trimming, cutting, splitting video
- Merging multiple videos or video+audio
- Resolution/bitrate/framerate changes
- Subtitle operations (add, extract, burn-in)
- Batch video processing
- Hardware-accelerated encoding

**DO NOT use ffmpeg for:**
- Downloading from YouTube, Vimeo, social media → Use `media-downloader` agent (yt-dlp)
- Extracting videos from web player URLs → Use `media-downloader` agent
- Any URL-based video acquisition → Use `media-downloader` agent

**Typical workflow:** `media-downloader` (acquire) → `ffmpeg` (process)

## Quick Reference

| Task | Command |
|------|---------|
| Convert container | `ffmpeg -i input.mov -c copy output.mp4` |
| Compress (HW) | `ffmpeg -hwaccel videotoolbox -i in.mp4 -c:v hevc_videotoolbox -q:v 75 -tag:v hvc1 out.mp4` |
| Compress (SW) | `ffmpeg -i in.mp4 -c:v libx264 -crf 23 out.mp4` |
| Extract audio | `ffmpeg -i video.mp4 -vn -c:a copy audio.m4a` |
| Trim | `ffmpeg -i in.mp4 -ss 00:01:00 -t 00:00:30 -c copy out.mp4` |
| Merge video+audio | `ffmpeg -i video.mp4 -i audio.m4a -c copy out.mp4` |
| Scale to 720p | `ffmpeg -i in.mp4 -vf "scale=-1:720" out.mp4` |
| Add subtitles | `ffmpeg -i in.mp4 -vf "subtitles=subs.srt" out.mp4` |
| Extract frame | `ffmpeg -i in.mp4 -ss 00:00:05 -frames:v 1 thumb.png` |

## Hardware Acceleration (Apple Silicon)

**M3 Pro VideoToolbox encoding is 7-10x faster with 90% less CPU.**

### Decode Acceleration
Always add before `-i`:
```bash
ffmpeg -hwaccel videotoolbox -i input.mp4 ...
```

### Encode Options

**H.265/HEVC (best compression, recommended):**
```bash
ffmpeg -hwaccel videotoolbox -i input.mp4 \
  -c:v hevc_videotoolbox -q:v 75 -tag:v hvc1 \
  -c:a aac output.mp4
```

**H.264 (maximum compatibility):**
```bash
ffmpeg -hwaccel videotoolbox -i input.mp4 \
  -c:v h264_videotoolbox -q:v 75 \
  -c:a aac output.mp4
```

### Quality Settings

| Type | Parameter | Scale | Typical |
|------|-----------|-------|---------|
| Hardware | `-q:v` | 1-100 (higher=better) | 75 |
| Software | `-crf` | 0-51 (lower=better) | 23 |

**Hardware does NOT support:** `-crf`, `-preset` (these are software-only)

### Verify Hardware Active
- CPU 20-30% = Hardware working
- CPU 100-400% = Software fallback

## Common Workflows

### 1. Convert Format (No Quality Loss)
```bash
ffmpeg -i input.mov -c copy output.mp4
```

### 2. Compress for Sharing
```bash
# Hardware (fast)
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v hevc_videotoolbox -q:v 70 -c:a aac -b:a 128k compressed.mp4

# Software (best quality)
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k compressed.mp4
```

### 3. Extract Audio
```bash
# Copy (fastest, keeps original format)
ffmpeg -i video.mp4 -vn -c:a copy audio.m4a

# Convert to MP3
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3
```

### 4. Trim Video
```bash
# Fast trim (may have keyframe issues)
ffmpeg -i input.mp4 -ss 00:01:00 -t 00:00:30 -c copy clip.mp4

# Accurate trim (re-encodes)
ffmpeg -i input.mp4 -ss 00:01:00 -t 00:00:30 -c:v libx264 -c:a aac clip.mp4
```

### 5. Merge Video + Audio
```bash
ffmpeg -i video.mp4 -i audio.m4a -c copy merged.mp4
```

### 6. Concatenate Videos
```bash
# Create list.txt:
# file 'video1.mp4'
# file 'video2.mp4'
ffmpeg -f concat -safe 0 -i list.txt -c copy combined.mp4
```

### 7. Scale/Resize
```bash
# To 720p (maintain aspect)
ffmpeg -i input.mp4 -vf "scale=-1:720" output.mp4

# To 1080p
ffmpeg -i input.mp4 -vf "scale=-1:1080" output.mp4
```

## Shell Aliases (Recommended)

Add to `~/.zshrc`:
```bash
export FFMPEG_QUALITY=75

# Hardware H.265 (recommended)
alias ffmpeg-hw='ffmpeg -hwaccel videotoolbox -c:v hevc_videotoolbox -q:v ${FFMPEG_QUALITY:-75} -tag:v hvc1'

# Hardware H.264 (compatibility)
alias ffmpeg-hw264='ffmpeg -hwaccel videotoolbox -c:v h264_videotoolbox -q:v ${FFMPEG_QUALITY:-75}'

# High quality
alias ffmpeg-hq='ffmpeg -hwaccel videotoolbox -c:v hevc_videotoolbox -q:v 85 -tag:v hvc1'

# Software encode
alias ffmpeg-sw='ffmpeg -c:v libx264 -crf 23 -preset medium'

# Quick copy
alias ffmpeg-copy='ffmpeg -c copy'
```

**Usage:**
```bash
ffmpeg-hw -i input.mov output.mp4
ffmpeg-hq -i input.mov high_quality.mp4
```

## Error Quick Reference

| Error | Solution |
|-------|----------|
| "Invalid data found" | Re-encode instead of `-c copy` |
| High CPU (100%+) | Check `-hwaccel videotoolbox` before `-i` |
| H.265 won't play | Add `-tag:v hvc1` for QuickTime compatibility |
| Seek inaccurate | Put `-ss` after `-i` or re-encode |
| Audio out of sync | Remove `-c copy`, re-encode audio |

## Detailed References

For comprehensive information, see `references/` directory:
- `codec-guide.md` - Codec comparison, containers, quality settings
- `hardware-accel.md` - Full VideoToolbox configuration
- `recipes.md` - Extended command recipes for all scenarios

## Integration with media-downloader

**Typical post-download workflow:**

```bash
# 1. Download with media-downloader agent
# (uses yt-dlp, saves to configured output directory)

# 2. Process with ffmpeg
# Compress large download:
ffmpeg -hwaccel videotoolbox -i downloaded.mp4 -c:v hevc_videotoolbox -q:v 70 compressed.mp4

# Extract audio:
ffmpeg -i downloaded.mp4 -vn -c:a copy audio.m4a

# Trim specific section:
ffmpeg -i downloaded.mp4 -ss 00:05:00 -t 00:02:00 -c copy clip.mp4
```
