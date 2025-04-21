import os
import math
import numpy as np
from PIL import Image
import image_tools

def calculate_entropy(pixel_values):
    """Calculate the entropy of the image."""
    # Count occurrences of each pixel value
    pixel_counts = {}
    total_pixels = len(pixel_values)
    
    for pixel in pixel_values:
        if pixel in pixel_counts:
            pixel_counts[pixel] += 1
        else:
            pixel_counts[pixel] = 1
    
    # Calculate entropy
    entropy = 0
    for count in pixel_counts.values():
        probability = count / total_pixels
        entropy -= probability * math.log2(probability)
    
    return entropy

def compress_lzw(data):
    """Compress a list of pixel values using LZW algorithm."""
    # Build the dictionary
    dict_size = 256
    dictionary = {chr(i): i for i in range(dict_size)}
    
    # Ensure data is not empty
    if not data:
        return []
    
    w = chr(data[0])
    result = []
    
    for i in range(1, len(data)):
        c = chr(data[i])
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            # Add wc to the dictionary
            if dict_size < 4096:  # Limit dictionary size to 12-bit codes
                dictionary[wc] = dict_size
                dict_size += 1
            w = c
    
    # Output the code for w
    if w:
        result.append(dictionary[w])
    
    return result

def main():
    # Read the image file
    image_path = "small_image.bmp"
    img = image_tools.readPILimg(image_path)
    
    # Ensure the image is in RGB mode
    if img.mode != "RGB":
        print(f"Converting image to RGB mode")
        img = img.convert("RGB")
    
    print(f"Processing color image. Size: {img.size}")
    
    # Get image dimensions
    width, height = img.size
    
    # Convert image to pixel values
    img_array = image_tools.PIL2np(img)
    
    # Split the image into R, G, B channels
    r_channel = img_array[:, :, 0].flatten().tolist()
    g_channel = img_array[:, :, 1].flatten().tolist()
    b_channel = img_array[:, :, 2].flatten().tolist()
    
    # Calculate entropy for each channel
    r_entropy = calculate_entropy(r_channel)
    g_entropy = calculate_entropy(g_channel)
    b_entropy = calculate_entropy(b_channel)
    
    print(f"Red channel entropy: {r_entropy:.4f} bits/pixel")
    print(f"Green channel entropy: {g_entropy:.4f} bits/pixel")
    print(f"Blue channel entropy: {b_entropy:.4f} bits/pixel")
    
    # Compress each channel
    r_compressed = compress_lzw(r_channel)
    g_compressed = compress_lzw(g_channel)
    b_compressed = compress_lzw(b_channel)
    
    # Calculate average code length for each channel
    code_length = 12  # Standard LZW code length
    r_avg_code_length = (len(r_compressed) * code_length) / len(r_channel)
    g_avg_code_length = (len(g_compressed) * code_length) / len(g_channel)
    b_avg_code_length = (len(b_compressed) * code_length) / len(b_channel)
    
    print(f"Red channel average code length: {r_avg_code_length:.4f} bits/pixel")
    print(f"Green channel average code length: {g_avg_code_length:.4f} bits/pixel")
    print(f"Blue channel average code length: {b_avg_code_length:.4f} bits/pixel")
    
    # Save compressed data and image dimensions
    compressed_file_path = os.path.splitext(image_path)[0] + "_color_compressed.lzw"
    with open(compressed_file_path, 'wb') as f:
        # Write image dimensions
        f.write(width.to_bytes(2, byteorder='big'))
        f.write(height.to_bytes(2, byteorder='big'))
        
        # Write the length of each compressed channel
        f.write(len(r_compressed).to_bytes(4, byteorder='big'))
        f.write(len(g_compressed).to_bytes(4, byteorder='big'))
        f.write(len(b_compressed).to_bytes(4, byteorder='big'))
        
        # Write compressed data for each channel
        for code in r_compressed:
            f.write(code.to_bytes(2, byteorder='big'))
        for code in g_compressed:
            f.write(code.to_bytes(2, byteorder='big'))
        for code in b_compressed:
            f.write(code.to_bytes(2, byteorder='big'))
    
    # Calculate compression ratio
    original_size = os.path.getsize(image_path)
    compressed_size = os.path.getsize(compressed_file_path)
    compression_ratio = compressed_size / original_size
    compression_factor = original_size / compressed_size
    space_saving = 1 - compression_ratio
    
    print(f"Original file size: {original_size} bytes")
    print(f"Compressed file size: {compressed_size} bytes")
    print(f"Compression Ratio (CR): {compression_ratio:.4f}")
    print(f"Compression Factor (CF): {compression_factor:.4f}")
    print(f"Space Saving (SS): {space_saving:.4f} ({space_saving*100:.2f}%)")
    
    print(f"Image compressed and saved as {compressed_file_path}")

if __name__ == "__main__":
    main() 