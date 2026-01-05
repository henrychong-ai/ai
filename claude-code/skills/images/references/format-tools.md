# Specialized Format Tools

Dedicated CLI tools for WebP, HEIF/HEIC, and SVG formats. These tools are faster and more feature-complete than ImageMagick for their specific formats.

## WebP Tools

WebP is Google's modern image format offering superior compression for web use.

### Installation Check

```bash
# Verify installed
which cwebp dwebp

# Install if missing
brew install webp
```

### Available Commands

| Command | Purpose |
|---------|---------|
| `cwebp` | Convert to WebP |
| `dwebp` | Convert from WebP |
| `gif2webp` | Convert GIF to animated WebP |
| `img2webp` | Create animated WebP from images |
| `webpinfo` | Get WebP file information |
| `webpmux` | Manipulate WebP containers |

### Convert TO WebP

```bash
# Basic conversion
cwebp input.png -o output.webp

# With quality (0-100, default 75)
cwebp -q 80 input.png -o output.webp

# Lossless
cwebp -lossless input.png -o output.webp

# Near-lossless (0-100, 0=max preprocessing)
cwebp -near_lossless 60 input.png -o output.webp

# Resize during conversion
cwebp -resize 800 600 input.png -o output.webp

# Crop during conversion (x, y, width, height)
cwebp -crop 10 10 100 100 input.png -o output.webp

# Preset for specific content types
cwebp -preset photo input.jpg -o output.webp    # Photos
cwebp -preset picture input.png -o output.webp  # Digital pictures
cwebp -preset drawing input.png -o output.webp  # Line art
cwebp -preset icon input.png -o output.webp     # Small icons
cwebp -preset text input.png -o output.webp     # Text-heavy images
```

### Convert FROM WebP

```bash
# To PNG
dwebp input.webp -o output.png

# To PPM (raw format)
dwebp input.webp -ppm -o output.ppm

# To BMP
dwebp input.webp -bmp -o output.bmp

# Extract specific frame from animated WebP
dwebp -frame 5 animated.webp -o frame5.png
```

### Animated WebP

```bash
# Convert GIF to animated WebP
gif2webp input.gif -o output.webp

# With quality and compression settings
gif2webp -q 80 -m 6 input.gif -o output.webp

# Create animated WebP from image sequence
img2webp -d 100 frame1.png frame2.png frame3.png -o animated.webp
# -d = duration per frame in ms

# With different durations per frame
img2webp -d 100 frame1.png -d 200 frame2.png -d 100 frame3.png -o animated.webp

# Loop count (0 = infinite)
img2webp -loop 0 -d 100 *.png -o animated.webp
```

### WebP Information

```bash
# Get file info
webpinfo input.webp

# Detailed info
webpinfo -summary input.webp
```

### Batch Conversion

```bash
# All PNGs to WebP
for f in *.png; do cwebp -q 80 "$f" -o "${f%.png}.webp"; done

# All JPGs to WebP
for f in *.jpg; do cwebp -q 85 "$f" -o "${f%.jpg}.webp"; done

# All WebPs to PNG
for f in *.webp; do dwebp "$f" -o "${f%.webp}.png"; done
```

---

## HEIF/HEIC Tools

HEIF (High Efficiency Image Format) is used by Apple devices. HEIC is Apple's implementation.

### Installation Check

```bash
# Verify installed
which heif-convert heif-info

# Install if missing
brew install libheif
```

### Available Commands

| Command | Purpose |
|---------|---------|
| `heif-convert` | Convert HEIF/HEIC to other formats |
| `heif-enc` | Encode images to HEIF |
| `heif-dec` | Decode HEIF images |
| `heif-info` | Get HEIF file information |
| `heif-thumbnailer` | Extract thumbnails |

### Convert FROM HEIC (iPhone Photos)

```bash
# To JPEG (most common use case)
heif-convert input.HEIC output.jpg

# To PNG
heif-convert input.HEIC output.png

# With quality (for JPEG output)
heif-convert -q 90 input.HEIC output.jpg

# Extract all images from HEIF container
heif-convert input.HEIC output.jpg
# Creates output-1.jpg, output-2.jpg, etc. if multiple images
```

### Convert TO HEIF

```bash
# Basic encode
heif-enc input.png -o output.heif

# With quality (0-100)
heif-enc -q 80 input.png -o output.heif

# Lossless
heif-enc -L input.png -o output.heif

# Use AVIF codec (AV1-based, better compression)
heif-enc --avif input.png -o output.avif
```

### HEIF Information

```bash
# Get file info
heif-info input.HEIC

# Detailed dump
heif-info -d input.HEIC
```

### Extract Thumbnail

```bash
heif-thumbnailer input.HEIC thumbnail.jpg
```

### Batch Convert iPhone Photos

```bash
# Convert all HEIC to JPG
for f in *.HEIC; do heif-convert -q 90 "$f" "${f%.HEIC}.jpg"; done

# Also handle lowercase .heic
for f in *.heic; do heif-convert -q 90 "$f" "${f%.heic}.jpg"; done

# Convert and organize
mkdir -p converted
for f in *.HEIC *.heic 2>/dev/null; do
  [ -f "$f" ] && heif-convert -q 90 "$f" "converted/${f%.*}.jpg"
done
```

---

## SVG Tools

SVG (Scalable Vector Graphics) requires specialized rendering for conversion to raster formats.

### Installation Check

```bash
# Verify installed
which rsvg-convert

# Install if missing
brew install librsvg
```

### Convert SVG to Raster

```bash
# To PNG (default)
rsvg-convert input.svg -o output.png

# To JPEG
rsvg-convert -f jpeg input.svg -o output.jpg

# To PDF
rsvg-convert -f pdf input.svg -o output.pdf

# To PS (PostScript)
rsvg-convert -f ps input.svg -o output.ps
```

### Sizing Options

```bash
# Specific width (height auto-calculated)
rsvg-convert -w 800 input.svg -o output.png

# Specific height (width auto-calculated)
rsvg-convert -h 600 input.svg -o output.png

# Both (may distort if aspect ratio differs)
rsvg-convert -w 800 -h 600 input.svg -o output.png

# Scale factor (2x, 3x, etc.)
rsvg-convert --zoom=2 input.svg -o output@2x.png

# DPI for print
rsvg-convert -d 300 input.svg -o output.png
```

### Background Options

```bash
# White background (SVGs often have transparent bg)
rsvg-convert -b white input.svg -o output.png

# Specific color
rsvg-convert -b '#ff0000' input.svg -o output.png

# Keep transparency (default for PNG)
rsvg-convert input.svg -o output.png
```

### Batch Convert SVGs

```bash
# All SVGs to PNG at 2x
for f in *.svg; do
  rsvg-convert --zoom=2 "$f" -o "${f%.svg}.png"
done

# Generate multiple sizes
for f in *.svg; do
  base="${f%.svg}"
  rsvg-convert -w 16 "$f" -o "${base}-16.png"
  rsvg-convert -w 32 "$f" -o "${base}-32.png"
  rsvg-convert -w 64 "$f" -o "${base}-64.png"
  rsvg-convert -w 128 "$f" -o "${base}-128.png"
done
```

---

## Quick Reference Table

| From | To | Command |
|------|-----|---------|
| PNG/JPG → WebP | `cwebp -q 80 in.png -o out.webp` |
| WebP → PNG | `dwebp in.webp -o out.png` |
| GIF → WebP | `gif2webp in.gif -o out.webp` |
| HEIC → JPG | `heif-convert -q 90 in.HEIC out.jpg` |
| HEIC → PNG | `heif-convert in.HEIC out.png` |
| PNG → HEIF | `heif-enc -q 80 in.png -o out.heif` |
| PNG → AVIF | `heif-enc --avif in.png -o out.avif` |
| SVG → PNG | `rsvg-convert -w 800 in.svg -o out.png` |
| SVG → PDF | `rsvg-convert -f pdf in.svg -o out.pdf` |

## When to Use Which Tool

| Scenario | Tool | Why |
|----------|------|-----|
| General image work | ImageMagick | Most versatile |
| WebP optimization | cwebp/dwebp | Better quality control, faster |
| iPhone photos | heif-convert | Native HEIC support |
| SVG rendering | rsvg-convert | Accurate SVG rendering |
| Animated WebP | gif2webp/img2webp | Full animation support |
| AVIF encoding | heif-enc --avif | Modern, best compression |
