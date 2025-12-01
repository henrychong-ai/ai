# ffmpeg Codec & Container Guide

Comprehensive reference for video/audio codecs, containers, and quality settings.

## Video Codecs

### H.264 / AVC
**Encoder:** `libx264` (software), `h264_videotoolbox` (hardware)
- **Pros:** Universal compatibility, plays everywhere
- **Cons:** Larger files than H.265
- **Use for:** Maximum compatibility, streaming, web
- **Quality:** `-crf 18-23` (software), `-q:v 70-80` (hardware)

```bash
# Software
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium output.mp4

# Hardware
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v h264_videotoolbox -q:v 75 output.mp4
```

### H.265 / HEVC
**Encoder:** `libx265` (software), `hevc_videotoolbox` (hardware)
- **Pros:** 50% smaller files than H.264 at same quality
- **Cons:** Slower encode (software), less compatibility
- **Use for:** Storage, 4K content, archival
- **Quality:** `-crf 23-28` (software), `-q:v 70-80` (hardware)

```bash
# Software
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -preset medium output.mp4

# Hardware (add -tag:v hvc1 for QuickTime)
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v hevc_videotoolbox -q:v 75 -tag:v hvc1 output.mp4
```

### VP9
**Encoder:** `libvpx-vp9`
- **Pros:** Open source, good compression, YouTube native
- **Cons:** Slow encoding, limited hardware support
- **Use for:** YouTube uploads, WebM format

```bash
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 output.webm
```

### AV1
**Encoder:** `libaom-av1`, `libsvtav1`
- **Pros:** Best compression (30% better than HEVC)
- **Cons:** Very slow encode, limited playback support
- **Use for:** Future-proofing, bandwidth-critical applications
- **Note:** M3 Pro can decode AV1 but NOT encode

```bash
# SVT-AV1 (faster than libaom)
ffmpeg -i input.mp4 -c:v libsvtav1 -crf 30 output.mp4
```

### ProRes
**Encoder:** `prores_ks`
- **Pros:** High quality, Apple native, fast editing
- **Cons:** Large files, macOS/iOS only
- **Use for:** Video editing, Apple ecosystem

```bash
# ProRes 422 (standard)
ffmpeg -i input.mp4 -c:v prores_ks -profile:v 2 output.mov

# ProRes profiles: 0=Proxy, 1=LT, 2=422, 3=HQ
```

## Audio Codecs

### AAC
**Encoder:** `aac` (built-in), `libfdk_aac` (better quality)
- **Use for:** Universal audio, MP4 containers
- **Bitrate:** 128-256 kbps typical

```bash
ffmpeg -i input.mp4 -c:a aac -b:a 192k output.mp4
```

### MP3
**Encoder:** `libmp3lame`
- **Use for:** Legacy compatibility, audio-only files
- **Quality:** `-q:a 0-9` (0=best), or `-b:a 320k`

```bash
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3
```

### Opus
**Encoder:** `libopus`
- **Use for:** Best quality/size ratio, VoIP, WebM
- **Bitrate:** 64-128 kbps (excellent quality)

```bash
ffmpeg -i input.mp4 -c:a libopus -b:a 128k output.opus
```

### FLAC
**Encoder:** `flac`
- **Use for:** Lossless audio archival
- **Note:** Large files, no quality loss

```bash
ffmpeg -i input.wav -c:a flac output.flac
```

### AC3 / E-AC3
**Encoder:** `ac3`, `eac3`
- **Use for:** Surround sound, DVD/Blu-ray compatibility

```bash
ffmpeg -i input.mp4 -c:a ac3 -b:a 448k output.mp4
```

## Containers

| Container | Extension | Best Codecs | Use Case |
|-----------|-----------|-------------|----------|
| **MP4** | .mp4 | H.264, H.265, AAC | Universal, streaming |
| **MKV** | .mkv | Any | Multiple tracks, subtitles |
| **MOV** | .mov | ProRes, H.264, H.265, AAC | Apple ecosystem |
| **WebM** | .webm | VP9, AV1, Opus | Web browsers |
| **AVI** | .avi | Various (legacy) | Old Windows |
| **M4A** | .m4a | AAC, ALAC | Audio-only MP4 |
| **MKA** | .mka | Any audio | Audio-only MKV |

### Container Conversion (No Re-encode)
```bash
# MOV to MP4
ffmpeg -i input.mov -c copy output.mp4

# MP4 to MKV
ffmpeg -i input.mp4 -c copy output.mkv

# Note: -c copy only works if codecs are compatible with target container
```

## Quality Settings Deep Dive

### Software Encoding (CRF)

**CRF (Constant Rate Factor):** 0-51 scale, lower = better quality

| CRF | Quality | Use Case |
|-----|---------|----------|
| 0 | Lossless | Archival (huge files) |
| 18 | Visually lossless | High quality archive |
| 23 | Default | Good balance |
| 28 | Lower quality | Small files |
| 51 | Worst | Tiny files |

**Preset:** Speed/compression tradeoff

| Preset | Speed | Compression |
|--------|-------|-------------|
| ultrafast | Fastest | Worst |
| superfast | | |
| veryfast | | |
| faster | | |
| fast | | |
| medium | Default | Default |
| slow | | |
| slower | | |
| veryslow | Slowest | Best |

```bash
# High quality, slow
ffmpeg -i input.mp4 -c:v libx264 -crf 18 -preset slow output.mp4

# Fast, larger file
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset fast output.mp4
```

### Hardware Encoding (VideoToolbox)

**Quality (-q:v):** 1-100 scale, higher = better quality

| -q:v | Quality | Use Case |
|------|---------|----------|
| 100 | Best | High quality archive |
| 85 | High | Quality-focused |
| 75 | Good | Balanced (default) |
| 65 | Medium | Size-focused |
| 50 | Low | Maximum compression |

```bash
# High quality
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v hevc_videotoolbox -q:v 85 -tag:v hvc1 output.mp4

# Balanced
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v hevc_videotoolbox -q:v 75 -tag:v hvc1 output.mp4
```

### Bitrate Control

**Constant Bitrate (CBR):**
```bash
ffmpeg -i input.mp4 -c:v libx264 -b:v 5M output.mp4
```

**Variable Bitrate (VBR) with max:**
```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -maxrate 5M -bufsize 10M output.mp4
```

**Two-pass (best for target size):**
```bash
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -f null /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 2 output.mp4
```

## Codec Comparison Summary

| Codec | File Size | Encode Speed | Compatibility | Recommendation |
|-------|-----------|--------------|---------------|----------------|
| H.264 | Large | Fast (HW) | Excellent | Default choice |
| H.265 | Medium | Fast (HW) | Good | Storage/4K |
| VP9 | Medium | Slow | Good (web) | YouTube/WebM |
| AV1 | Small | Very slow | Limited | Future use |
| ProRes | Very large | Fast | macOS only | Editing |
