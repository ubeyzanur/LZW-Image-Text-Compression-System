import os
import numpy as np
from PIL import Image
import image_tools

def compress_lzw(data):
    """Compress a list of pixel values using LZW algorithm."""
    if not data: return []
    
    dict_size = 256
    dictionary = {(i,): i + 128 for i in range(-128, 128)}
    
    result = []
    w = (data[0],)
    
    for i in range(1, len(data)):
        c = (data[i],)
        wc = w + c
        
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            if dict_size < 4096:
                dictionary[wc] = dict_size
                dict_size += 1
            w = c
    
    if w: result.append(dictionary[w])
    return result

def main():
    # Read the image file
    image_path = "small_image.bmp"
    img = image_tools.readPILimg(image_path)
    
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    width, height = img.size
    img_array = image_tools.PIL2np(img)
    
    # Process each channel
    compressed_data = []
    
    for i in range(3):
        channel = img_array[:, :, i]
        
        # Create difference image
        diff_array = np.zeros((height, width), dtype=np.int16)
        diff_array[0, 0] = channel[0, 0]
        
        # Row-wise differences
        for r in range(height):
            for c in range(1, width):
                diff_array[r, c] = int(channel[r, c]) - int(channel[r, c-1])
        
        # Column-wise differences for first column
        for r in range(1, height):
            diff_array[r, 0] = int(channel[r, 0]) - int(channel[r-1, 0])
        
        # Flatten and clip values
        diff_values = diff_array.flatten().tolist()
        diff_values = [max(-128, min(127, x)) for x in diff_values]
        
        # Compress
        compressed = compress_lzw(diff_values)
        compressed_data.append(compressed)
    
    # Save compressed data
    compressed_file_path = os.path.splitext(image_path)[0] + "_color_diff_compressed.lzw"
    with open(compressed_file_path, 'wb') as f:
        # Write image dimensions
        f.write(width.to_bytes(2, byteorder='big'))
        f.write(height.to_bytes(2, byteorder='big'))
        
        # Write compressed channel lengths
        for compressed in compressed_data:
            f.write(len(compressed).to_bytes(4, byteorder='big'))
        
        # Write compressed data
        for compressed in compressed_data:
            for code in compressed:
                f.write(code.to_bytes(2, byteorder='big'))
    
    # Calculate compression metrics
    original_size = os.path.getsize(image_path)
    compressed_size = os.path.getsize(compressed_file_path)
    compression_ratio = compressed_size / original_size
    
    print(f"Original: {original_size} bytes, Compressed: {compressed_size} bytes")
    print(f"Compression Ratio: {compression_ratio:.4f}")
    print(f"Space Saving: {(1-compression_ratio)*100:.2f}%")
    print(f"Image compressed and saved as {compressed_file_path}")

if __name__ == "__main__":
    main() 