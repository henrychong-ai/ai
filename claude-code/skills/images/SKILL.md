---
name: images
description: This skill should be used for image manipulation including combining, resizing, cropping, format conversion, compression, and batch processing. Covers ImageMagick v7 commands (magick), collages, montages, and optimization. Triggers: combine images, resize image, convert format, image collage, crop image, compress image, watermark, image processing.
---

# Images

Image manipulation skill using ImageMagick v7 and native macOS tools.

## Installation Check

```bash
# Verify ImageMagick installed
magick -version

# Install if missing
brew install imagemagick
```

**Note:** ImageMagick v7 uses `magick` command. The old `convert` command is deprecated.

## Quick Reference

| Task | Command |
|------|---------|
| Combine horizontal | `magick img1.png img2.png +append out.png` |
| Combine vertical | `magick img1.png img2.png -append out.png` |
| Resize to width | `magick in.png -resize 800x out.png` |
| Resize to height | `magick in.png -resize x600 out.png` |
| Resize percentage | `magick in.png -resize 50% out.png` |
| Convert format | `magick in.png out.jpg` |
| Compress JPEG | `magick in.jpg -quality 80 out.jpg` |
| Crop | `magick in.png -crop 100x100+10+10 out.png` |
| Grid collage | `magick montage *.png -geometry +5+5 -tile 3x3 out.png` |
| Add border | `magick in.png -border 10x10 -bordercolor white out.png` |
| Rotate | `magick in.png -rotate 90 out.png` |
| Get info | `magick identify in.png` |

## Common Workflows

### Combine Images Side-by-Side (Horizontal)
```bash
magick left.png right.png +append combined.png
```

### Combine Images Top-to-Bottom (Vertical)
```bash
magick top.png bottom.png -append combined.png
```

### Create Grid Collage
```bash
# 3x3 grid with 5px gaps
magick montage *.png -geometry +5+5 -tile 3x3 collage.png

# Specific size per image
magick montage *.png -geometry 300x300+5+5 -tile 3x3 collage.png
```

### Batch Convert Format
```bash
# PNG to JPEG
for f in *.png; do magick "$f" "${f%.png}.jpg"; done

# With compression
for f in *.png; do magick "$f" -quality 85 "${f%.png}.jpg"; done
```

### Resize Preserving Aspect Ratio
```bash
# Fit within 1920x1080, maintain aspect
magick in.png -resize 1920x1080 out.png

# Force exact dimensions (may distort)
magick in.png -resize 1920x1080! out.png
```

## macOS Native Alternative: sips

For simple operations, macOS `sips` is faster (no install needed):

```bash
# Resize
sips -Z 800 image.png    # Max dimension 800px

# Convert format
sips -s format jpeg image.png --out image.jpg

# Get info
sips -g all image.png
```

## Format-Specific Tools

For specific formats, dedicated tools are faster than ImageMagick:

| Format | Tool | Example |
|--------|------|---------|
| WebP | `cwebp`/`dwebp` | `cwebp -q 80 in.png -o out.webp` |
| HEIC (iPhone) | `heif-convert` | `heif-convert photo.HEIC photo.jpg` |
| SVG | `rsvg-convert` | `rsvg-convert -w 800 in.svg -o out.png` |

## Detailed References

- `references/imagemagick.md` - Full ImageMagick command reference
- `references/format-tools.md` - WebP, HEIF/HEIC, and SVG tools
