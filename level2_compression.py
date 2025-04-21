import os
import math
import numpy as np
from PIL import Image
import image_tools
import cv2

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
    """LZW compression algorithm"""
    # Initialize dictionary - for numerical data
    dictionary = {i: i for i in range(256)}
    
    if not data:
        return []
    
    w = data[0]
    result = []
    next_code = 256
    max_code = 65535  # 16-bit limit
    
    # Compression process
    for c in data[1:]:
        wc = (w, c)
        if wc in dictionary:
            w = dictionary[wc]
        else:
            result.append(w)
            # Dictionary size check
            if next_code < max_code:
                dictionary[wc] = next_code
                next_code += 1
            w = c
    
    # Add the last remaining w value
    result.append(w)
    
    return result

def compress_image_file(input_file_path):
    # Read the image
    img = cv2.imread(input_file_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print("Could not read image!")
        return None
    
    # Image dimensions
    height, width = img.shape
    print(f"Image dimensions: {width}x{height}")
    
    # Flatten the image and convert to list
    flat_img = img.flatten().tolist()
    
    # LZW compression
    try:
        compressed_data = compress_lzw(flat_img)
        
        # Save the compressed data
        output_file_path = os.path.splitext(input_file_path)[0] + "_compressed.lzw"
        with open(output_file_path, 'wb') as f:
            # Write width and height (4 bytes each)
            f.write(width.to_bytes(4, byteorder='big'))
            f.write(height.to_bytes(4, byteorder='big'))
            
            # Write compressed data - USE ONLY 2 BYTES!
            for value in compressed_data:
                # Use 16-bit (2 bytes) to prevent overflow
                if value > 65535:
                    value = 65535  # Limit if value is too large
                f.write(value.to_bytes(2, byteorder='big'))
        
        print(f"Image compressed successfully: {output_file_path}")
        return output_file_path
    
    except Exception as e:
        print(f"Compression error: {e}")
        return None

def main():
    # Read the image file
    image_path = "small_image_grayscale.bmp"
    img = image_tools.readPILimg(image_path)
    
    # Convert to grayscale if not already
    if img.mode != "L":
        img = image_tools.color2gray(img)
        print(f"Image converted to grayscale. Size: {img.size}")
    else:
        print(f"Image is already grayscale. Size: {img.size}")
    
    # Get image dimensions
    width, height = img.size
    
    # Convert image to pixel values
    img_array = image_tools.PIL2np(img)
    pixel_values = img_array.flatten().tolist()
    
    print(f"Original image dimensions: {width}x{height}")
    print(f"Total pixels: {len(pixel_values)}")
    
    # Calculate entropy of original image
    entropy = calculate_entropy(pixel_values)
    print(f"Image entropy: {entropy:.4f} bits/pixel")
    
    # Compress the pixel values (construct LZW dictionary)
    compressed_codes = compress_lzw(pixel_values)
    
    # Calculate average code length
    code_length = 12  # Standard LZW code length
    avg_code_length = (len(compressed_codes) * code_length) / len(pixel_values)
    print(f"Average code length: {avg_code_length:.4f} bits/pixel")
    
    # Save compressed data and image dimensions
    compressed_file_path = os.path.splitext(image_path)[0] + "_compressed.lzw"
    with open(compressed_file_path, 'wb') as f:
        f.write(width.to_bytes(4, byteorder='big'))
        f.write(height.to_bytes(4, byteorder='big'))
        
        for value in compressed_codes:
            f.write(value.to_bytes(4, byteorder='big'))  # 4 byte kullandığınızdan emin olun
    
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