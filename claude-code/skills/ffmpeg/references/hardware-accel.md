# ffmpeg Hardware Acceleration on Apple Silicon

Complete guide to VideoToolbox hardware acceleration on M3 Pro MacBook.

## Overview

**VideoToolbox** is Apple's low-level hardware video encoding/decoding framework that provides direct access to the dedicated Media Engine in Apple Silicon chips.

### Performance Benefits
- **Speed:** 7-10x faster than software encoding
- **CPU Usage:** 20-30% (vs 100-400% software)
- **Power:** Minimal battery drain
- **Heat:** Cool and quiet operation

### M3 Pro Capabilities
- **Hardware Encode:** H.264, H.265/HEVC, ProRes
- **Hardware Decode:** H.264, H.265/HEVC, ProRes, AV1
- **Note:** AV1 decode only, no encode support

## Basic Usage

### Enable Hardware Decode
Always add `-hwaccel videotoolbox` BEFORE `-i`:
```bash
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v libx264 output.mp4
#      ^^^^^^^^^^^^^^^^^^^^^^ decode acceleration
```

### Hardware Encode

**H.265/HEVC (recommended):**
```bash
ffmpeg -hwaccel videotoolbox -i input.mp4 \
  -c:v hevc_videotoolbox \
  -q:v 75 \
  -tag:v hvc1 \
  -c:a aac \
  output.mp4
```

**H.264 (maximum compatibility):**
```bash
ffmpeg -hwaccel videotoolbox -i input.mp4 \
  -c:v h264_videotoolbox \
  -q:v 75 \
  -c:a aac \
  output.mp4
```

## Quality Control

### VideoToolbox Quality Scale
**Parameter:** `-q:v` (1-100, higher = better)

| Value | Quality | File Size | Use Case |
|-------|---------|-----------|----------|
| 100 | Maximum | Largest | Archival |
| 85 | High | Large | Quality priority |
| 75 | Good | Medium | **Recommended default** |
| 65 | Medium | Smaller | Size priority |
| 50 | Low | Smallest | Maximum compression |

### Important: Incompatible Parameters
VideoToolbox does **NOT** support these software-only parameters:
- `-crf` (use `-q:v` instead)
- `-preset` (no equivalent)
- `-tune` (no equivalent)

```bash
# WRONG - will be ignored
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v hevc_videotoolbox -crf 23 output.mp4

# CORRECT
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v hevc_videotoolbox -q:v 75 output.mp4
```

### Alternative: Bitrate Control
```bash
# Constant bitrate
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v hevc_videotoolbox -b:v 5M output.mp4

# Variable with max
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v hevc_videotoolbox -b:v 5M -maxrate 8M output.mp4
```

## Advanced Options

### 10-bit Encoding
```bash
ffmpeg -hwaccel videotoolbox -i input.mp4 \
  -c:v hevc_videotoolbox \
  -q:v 75 \
  -pix_fmt p010le \
  -profile:v 2 \
  -tag:v hvc1 \
  output.mp4
```

### B-frames Control
```bash
ffmpeg -hwaccel videotoolbox -i input.mp4 \
  -c:v h264_videotoolbox \
  -q:v 75 \
  -bf 3 \
  output.mp4
```

### Keyframe Interval
```bash
ffmpeg -hwaccel videotoolbox -i input.mp4 \
  -c:v hevc_videotoolbox \
  -q:v 75 \
  -g 60 \
  output.mp4
# -g 60 = keyframe every 60 frames (2 seconds at 30fps)
```

## Shell Configuration

### Environment Variable
```bash
# Add to ~/.zshrc
export FFMPEG_QUALITY=75
```

### Recommended Aliases
```bash
# Add to ~/.zshrc

# Hardware H.265 (best balance)
alias ffmpeg-hw='ffmpeg -hwaccel videotoolbox -c:v hevc_videotoolbox -q:v ${FFMPEG_QUALITY:-75} -tag:v hvc1'

# Hardware H.264 (compatibility)
alias ffmpeg-hw264='ffmpeg -hwaccel videotoolbox -c:v h264_videotoolbox -q:v ${FFMPEG_QUALITY:-75}'

# High quality
alias ffmpeg-hq='ffmpeg -hwaccel videotoolbox -c:v hevc_videotoolbox -q:v 85 -tag:v hvc1'

# Software fallback
alias ffmpeg-sw='ffmpeg -c:v libx264 -crf 23 -preset medium'

# Quick copy (no encode)
alias ffmpeg-copy='ffmpeg -c copy'

# Audio extraction
alias ffmpeg-audio='ffmpeg -vn -c:a copy'
```

### Apply Configuration
```bash
source ~/.zshrc
```

### Usage Examples
```bash
# Basic hardware encode
ffmpeg-hw -i input.mov output.mp4

# High quality
ffmpeg-hq -i input.mov archive.mp4

# Quick container change
ffmpeg-copy -i input.mov output.mp4
```

## Verification & Troubleshooting

### Check Hardware Availability
```bash
ffmpeg -hwaccels
# Should output: videotoolbox
```

### Check Encoder Availability
```bash
ffmpeg -encoders | grep videotoolbox
# Should show: h264_videotoolbox, hevc_videotoolbox
```

### Verify Hardware Active During Encode
Monitor CPU usage:
- **20-30% CPU** = Hardware acceleration working
- **100-400% CPU** = Software fallback (problem!)

Check with Activity Monitor or:
```bash
# Run encode in background, then:
top -pid $(pgrep ffmpeg)
```

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| High CPU (100%+) | Hardware not active | Ensure `-hwaccel videotoolbox` before `-i` |
| "Unknown encoder" | Old ffmpeg | `brew upgrade ffmpeg` |
| H.265 won't play | Missing tag | Add `-tag:v hvc1` |
| Quality too low | Wrong parameter | Use `-q:v 75` not `-crf` |
| Encode fails | Unsupported input | Try decode-only acceleration |

### Fallback Strategy
If hardware fails, fall back to software:
```bash
# Try hardware first
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v hevc_videotoolbox -q:v 75 -tag:v hvc1 output.mp4

# If fails, use software
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -preset medium output.mp4
```

## Performance Comparison

### M3 Pro Benchmarks (Typical)

| Task | Hardware | Software | Speedup |
|------|----------|----------|---------|
| 1080p H.264 encode | 400 fps | 60 fps | 6.7x |
| 1080p H.265 encode | 350 fps | 40 fps | 8.8x |
| 4K H.264 encode | 120 fps | 15 fps | 8x |
| 4K H.265 encode | 100 fps | 10 fps | 10x |
| Stream copy | 1650x realtime | N/A | N/A |

### Quality vs Speed Tradeoff

| Method | Speed | Quality | File Size |
|--------|-------|---------|-----------|
| HW q:v 75 | Fastest | Good | Medium |
| HW q:v 85 | Fast | High | Large |
| SW crf 23 medium | Slow | Good | Small |
| SW crf 18 slow | Slowest | Best | Medium |

**Recommendation:** Use hardware for speed, software for maximum quality/compression.

## VideoToolbox Technical Details

### Framework Components
- **VTCompressionSession:** Hardware encoding
- **VTDecompressionSession:** Hardware decoding
- **VTPixelTransferSession:** Format conversion

### Supported Formats
**Encode:**
- H.264 (AVC)
- H.265 (HEVC)
- ProRes (all profiles)

**Decode:**
- H.264 (AVC)
- H.265 (HEVC)
- ProRes
- AV1 (M3 and later)
- VP9
- MPEG-2, MPEG-4

### Limitations
- Less quality tuning than software encoders
- 10-20% larger files at equivalent visual quality
- No AV1 encode support (decode only)
- Some advanced features unavailable (B-pyramid, etc.)

### When to Use Software Instead
- Archival requiring maximum compression
- Specific codec features needed
- Fine quality tuning required
- Batch processing where quality > speed
