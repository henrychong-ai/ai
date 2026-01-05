# ImageMagick v7 Complete Reference

Comprehensive command reference for ImageMagick v7 on macOS.

## Installation & Setup

```bash
# Install via Homebrew
brew install imagemagick

# Verify installation
magick -version

# Check supported formats
magick identify -list format

# Check available delegates (optional features)
magick identify -list delegate
```

## Core Commands

ImageMagick v7 consolidates all operations under `magick`:

| Command | Purpose |
|---------|---------|
| `magick` | Main command (replaces convert) |
| `magick identify` | Get image information |
| `magick montage` | Create composite images |
| `magick compare` | Compare two images |
| `magick composite` | Overlay images |
| `magick mogrify` | Batch modify in-place |
| `magick display` | View images (X11 required) |
| `magick animate` | View animation (X11 required) |

## Image Information

```bash
# Basic info (format, dimensions, size)
magick identify image.png

# Verbose info (all metadata)
magick identify -verbose image.png

# Specific properties
magick identify -format "%w x %h\n" image.png        # Dimensions
magick identify -format "%[colorspace]\n" image.png  # Color space
magick identify -format "%b\n" image.png             # File size
```

## Combining Images

### Append (Simple Combine)

```bash
# Horizontal (side by side) - +append
magick img1.png img2.png +append output.png
magick img1.png img2.png img3.png +append output.png  # Multiple

# Vertical (top to bottom) - -append
magick img1.png img2.png -append output.png

# With background color for size mismatches
magick img1.png img2.png -background white +append output.png
```

### Montage (Grid Layout)

```bash
# Basic grid
magick montage *.png output.png

# Specify tile layout (columns x rows)
magick montage *.png -tile 3x2 output.png      # 3 columns, 2 rows
magick montage *.png -tile 3x output.png       # 3 columns, auto rows
magick montage *.png -tile x3 output.png       # Auto columns, 3 rows

# With geometry (size + spacing)
magick montage *.png -geometry +5+5 output.png           # 5px gaps
magick montage *.png -geometry 200x200+5+5 output.png    # Resize to 200x200 with gaps
magick montage *.png -geometry 200x200+5+5^ output.png   # Fill 200x200 (crop overflow)

# With background and border
magick montage *.png -background gray -geometry +2+2 output.png
magick montage *.png -border 2 -bordercolor white output.png

# Labels
magick montage *.png -label '%f' output.png              # Filename as label
magick montage *.png -label '%wx%h' output.png           # Dimensions as label
```

### Composite (Overlay)

```bash
# Place overlay on base image
magick composite overlay.png base.png output.png

# With position
magick composite -geometry +100+50 overlay.png base.png output.png

# With transparency
magick composite -dissolve 50% overlay.png base.png output.png

# Watermark (bottom-right corner)
magick composite -gravity southeast -geometry +10+10 watermark.png base.png output.png
```

## Resizing

```bash
# Fit within dimensions (maintain aspect ratio)
magick in.png -resize 800x600 out.png

# Fit width only
magick in.png -resize 800x out.png

# Fit height only
magick in.png -resize x600 out.png

# Force exact dimensions (may distort)
magick in.png -resize 800x600! out.png

# Percentage
magick in.png -resize 50% out.png

# Only shrink (don't enlarge)
magick in.png -resize 800x600\> out.png

# Only enlarge (don't shrink)
magick in.png -resize 800x600\< out.png

# Fill area and crop overflow
magick in.png -resize 800x600^ -gravity center -extent 800x600 out.png

# Thumbnail (fast, good for previews)
magick in.png -thumbnail 200x200 out.png
```

## Cropping

```bash
# Basic crop: WIDTHxHEIGHT+X+Y
magick in.png -crop 100x100+50+50 out.png    # 100x100 starting at (50,50)

# Crop from center
magick in.png -gravity center -crop 100x100+0+0 out.png

# Crop percentage
magick in.png -crop 50%x50% out.png

# Trim whitespace/borders
magick in.png -trim out.png

# Trim with fuzz (tolerance for near-white)
magick in.png -fuzz 10% -trim out.png

# Shave (remove from edges)
magick in.png -shave 10x10 out.png           # 10px from all sides
```

## Format Conversion

```bash
# Simple conversion (by extension)
magick input.png output.jpg
magick input.jpg output.webp
magick input.png output.pdf

# JPEG quality (0-100)
magick in.png -quality 85 out.jpg

# PNG compression (0-9)
magick in.jpg -quality 90 out.png

# WebP quality
magick in.png -quality 80 out.webp

# Convert to specific color depth
magick in.png -depth 8 out.png

# Convert color space
magick in.png -colorspace Gray out.png       # Grayscale
magick in.png -colorspace sRGB out.png       # sRGB
magick in.png -colorspace CMYK out.tiff      # CMYK for print
```

## Compression & Optimization

```bash
# JPEG compression
magick in.jpg -quality 80 out.jpg
magick in.jpg -quality 80 -sampling-factor 4:2:0 out.jpg  # Chroma subsampling

# PNG optimization
magick in.png -strip -define png:compression-level=9 out.png

# Remove metadata (EXIF, etc.)
magick in.jpg -strip out.jpg

# Reduce colors (PNG)
magick in.png -colors 256 out.png
magick in.png -colors 16 out.png
```

## Transformations

```bash
# Rotate
magick in.png -rotate 90 out.png
magick in.png -rotate -45 out.png            # Counter-clockwise
magick in.png -rotate 45 -background white out.png  # With background

# Flip/Flop
magick in.png -flip out.png                  # Vertical mirror
magick in.png -flop out.png                  # Horizontal mirror

# Transpose/Transverse
magick in.png -transpose out.png             # Flip + rotate 90 CCW
magick in.png -transverse out.png            # Flip + rotate 90 CW
```

## Color Adjustments

```bash
# Brightness/Contrast
magick in.png -brightness-contrast 10x5 out.png  # +10% brightness, +5% contrast

# Levels (black point, gamma, white point)
magick in.png -level 10%,90%,1.0 out.png

# Auto-level (stretch histogram)
magick in.png -auto-level out.png

# Normalize (like auto-level but more aggressive)
magick in.png -normalize out.png

# Modulate (brightness, saturation, hue)
magick in.png -modulate 110,120,100 out.png  # +10% bright, +20% sat, no hue change

# Negate (invert colors)
magick in.png -negate out.png

# Colorize
magick in.png -fill blue -colorize 30% out.png
```

## Borders & Effects

```bash
# Add border
magick in.png -border 10x10 out.png
magick in.png -border 10x10 -bordercolor red out.png

# Add padding (extent with gravity)
magick in.png -gravity center -background white -extent 1000x1000 out.png

# Drop shadow
magick in.png \( +clone -background black -shadow 60x5+5+5 \) +swap \
  -background none -layers merge +repage out.png

# Rounded corners
magick in.png \( +clone -alpha extract -draw 'fill black polygon 0,0 0,15 15,0 fill white circle 15,15 15,0' \
  \( +clone -flip \) -compose Multiply -composite \
  \( +clone -flop \) -compose Multiply -composite \) \
  -alpha off -compose CopyOpacity -composite out.png

# Blur
magick in.png -blur 0x5 out.png

# Sharpen
magick in.png -sharpen 0x1 out.png
```

## Text & Annotations

```bash
# Add text
magick in.png -gravity south -pointsize 24 -fill white \
  -annotate +0+10 'Caption text' out.png

# Text with background
magick in.png -gravity south -background '#00000080' -fill white \
  -pointsize 20 label:'Caption' -append out.png

# Using specific font
magick -list font | grep -i arial    # Find fonts
magick in.png -font Arial -pointsize 24 -annotate +10+30 'Text' out.png
```

## Batch Processing

### Using mogrify (in-place)

```bash
# Resize all PNGs in place
magick mogrify -resize 800x800 *.png

# Convert all PNGs to JPG
magick mogrify -format jpg *.png

# Output to different directory
magick mogrify -path ./thumbnails -thumbnail 200x200 *.jpg
```

### Using loops

```bash
# Convert with custom naming
for f in *.png; do
  magick "$f" -resize 50% "small_${f}"
done

# Convert format
for f in *.png; do
  magick "$f" -quality 85 "${f%.png}.jpg"
done
```

## Special Filename Syntax

```bash
# Read from stdin
cat image.png | magick - output.png

# Write to stdout
magick input.png png:- | other_command

# Multi-page/frame selection
magick 'input.pdf[0]' output.png      # First page only
magick 'input.gif[0-3]' output.png    # Frames 0-3

# Inline image creation
magick -size 100x100 xc:red output.png           # Solid red
magick -size 100x100 gradient:white-black output.png  # Gradient
magick -size 100x100 plasma: output.png          # Plasma effect
```

## Error Handling

| Error | Solution |
|-------|----------|
| `unable to open image` | Check file path, permissions, or iCloud placeholder |
| `no decode delegate` | Format not supported, install delegate (e.g., `brew install ghostscript` for PDF) |
| `memory allocation failed` | Image too large, use `-limit memory 1GiB` |
| `improper image header` | Corrupted file or wrong extension |

## Performance Tips

```bash
# Limit memory usage
magick -limit memory 1GiB -limit map 2GiB in.png -resize 50% out.png

# Use temporary files for large operations
magick -limit memory 256MiB -limit disk 4GiB in.png -resize 50% out.png

# Parallel batch processing
ls *.png | parallel magick {} -resize 800x {.}_small.png
```

## Common Patterns

### Social Media Sizes

```bash
# Instagram square (1080x1080)
magick in.png -resize 1080x1080^ -gravity center -extent 1080x1080 instagram.png

# Twitter header (1500x500)
magick in.png -resize 1500x500^ -gravity center -extent 1500x500 twitter.png

# LinkedIn banner (1584x396)
magick in.png -resize 1584x396^ -gravity center -extent 1584x396 linkedin.png
```

### Favicon Generation

```bash
magick logo.png -resize 16x16 favicon-16.png
magick logo.png -resize 32x32 favicon-32.png
magick logo.png -resize 180x180 apple-touch-icon.png
magick favicon-16.png favicon-32.png favicon.ico
```

### Contact Sheet

```bash
magick montage *.jpg -thumbnail 200x200 -geometry +5+5 -tile 5x \
  -background white -title "Photo Contact Sheet" contact_sheet.pdf
```
