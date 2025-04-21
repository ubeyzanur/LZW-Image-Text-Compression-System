# LZW Image & Text Compression System

A comprehensive implementation of the Lempel-Ziv-Welch (LZW) compression algorithm, supporting multiple levels of compression for both text and image data with a user-friendly graphical interface.

## Features

- **Multi-level Compression**: 5 different compression levels for various data types
  - **Level 1**: Text compression
  - **Level 2**: Grayscale image compression
  - **Level 3**: Grayscale difference image compression
  - **Level 4**: Color image compression
  - **Level 5**: Color difference image compression

- **Difference-based Compression**: Advanced techniques using pixel differences to achieve higher compression ratios

- **Graphical User Interface**: User-friendly GUI for easy file selection, compression/decompression, and performance analysis

- **Comprehensive Metrics**: Detailed analysis including entropy calculation, compression ratio, and average code length

## Screenshots

![image](https://github.com/user-attachments/assets/2aa4b9ae-c3ab-44c7-af58-07aee0ece0d3)


## Requirements

- Python 3.6+
- NumPy
- PIL (Python Imaging Library)
- OpenCV (cv2)
- Tkinter

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/lzw-compression-system.git
cd lzw-compression-system

# Install dependencies
pip install numpy pillow opencv-python
```

## Usage

### Running the GUI

```bash
python lzw_gui.py
```

### Command-line Usage

#### Text Compression (Level 1)
```bash
python level1_compression.py
```

#### Grayscale Image Compression (Level 2)
```bash
python level2_compression.py
```

#### Grayscale Difference Image Compression (Level 3)
```bash
python level3_compression.py
```

#### Color Image Compression (Level 4)
```bash
python level4_compression.py
```

#### Color Difference Image Compression (Level 5)
```bash
python level5_compression.py
```

## Project Structure

```
├── lzw_gui.py              # Main GUI application
├── image_tools.py          # Image processing utilities
├── level1_compression.py   # Text compression
├── level1_decompression.py # Text decompression
├── level2_compression.py   # Grayscale image compression
├── level2_decompression.py # Grayscale image decompression
├── level3_compression.py   # Grayscale difference image compression
├── level3_decompression.py # Grayscale difference image decompression
├── level4_compression.py   # Color image compression
├── level4_decompression.py # Color image decompression
├── level5_compression.py   # Color difference image compression
└── level5_decompression.py # Color difference image decompression
```

## Compression Methods

### Text Compression (Level 1)
- Standard LZW dictionary-based compression
- Dynamic code length for optimal compression

### Grayscale Image Compression (Level 2)
- Direct compression of pixel values
- 8-bit grayscale support

### Grayscale Difference Image Compression (Level 3)
- Creates a difference image by calculating pixel-to-pixel variations
- Leverages lower entropy in difference images for better compression
- Typically achieves 30-40% better compression than Level 2

### Color Image Compression (Level 4)
- Separate compression of R, G, B channels
- Preserves full color information

### Color Difference Image Compression (Level 5)
- Creates difference images for each color channel
- Achieves the best compression ratio (typically 65-70% reduction)
- Maintains lossless quality

## Performance Metrics

| Level | Compression Method | Typical Compression Ratio | Space Saving |
|-------|-------------------|--------------------------|--------------|
| 1     | Text              | 0.5 - 0.7                | 30-50%       |
| 2     | Grayscale         | 0.6 - 0.8                | 20-40%       |
| 3     | Grayscale Diff    | 0.4 - 0.6                | 40-60%       |
| 4     | Color             | 0.7 - 0.9                | 10-30%       |
| 5     | Color Diff        | 0.3 - 0.5                | 50-70%       |

## Technical Details

### LZW Algorithm Implementation
- Dynamic dictionary with up to 4096 entries (12-bit codes)
- Special handling for difference values in the range -255 to +255
- Entropy-based performance evaluation

### Entropy Calculation
- Measures information content in the data
- Used to evaluate compression efficiency
- Lower entropy values indicate better compressibility
