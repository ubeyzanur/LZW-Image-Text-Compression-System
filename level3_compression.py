import os
import math
import numpy as np
from PIL import Image
import image_tools

def create_difference_image(img_array):
    """Create a difference image by taking row-wise and column-wise differences."""
    height, width = img_array.shape
    # Use int16 data type to handle negative differences
    diff_array = np.zeros((height, width), dtype=np.int16)
    
    # Copy the first pixel as is
    diff_array[0, 0] = img_array[0, 0]
    
    # Take row-wise differences (for each row, starting from the second pixel)
    for i in range(height):
        for j in range(1, width):
            diff_array[i, j] = int(img_array[i, j]) - int(img_array[i, j-1])
    
    # Take column-wise differences for the first column (starting from the second pixel)
    for i in range(1, height):
        diff_array[i, 0] = int(img_array[i, 0]) - int(img_array[i-1, 0])
    
    return diff_array

def compress_lzw(data):
    """Compress a list of pixel values using LZW algorithm with integer tuples."""
    # Ensure data is not empty
    if not data:
        return []
    
    # Build the dictionary with single values
    dict_size = 256
    dictionary = {}
    for i in range(-255, 256):
        dictionary[(i,)] = i + 128  # Map to 0-255 range
    
    result = []
    w = (data[0],)  # Start with the first value as a tuple
    
    for i in range(1, len(data)):
        c = (data[i],)  # Current value as a tuple
        wc = w + c  # Concatenate tuples
        
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            # Add wc to the dictionary if we haven't exceeded the limit
            if dict_size < 4096:  # Limit dictionary size to 12-bit codes
                dictionary[wc] = dict_size
                dict_size += 1
            w = c
    
    # Output the code for w
    if w:
        result.append(dictionary[w])
    
    # Print dictionary size for debugging
    print(f"Dictionary size: {len(dictionary)}")
    print(f"Min code: {min(result)}, Max code: {max(result)}")
    
    return result

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

def main():
    # Read the image file
    image_path = "big_image.bmp"
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
    
    # Create difference image
    diff_array = create_difference_image(img_array)
    
    # Save the difference image for debugging
    diff_img = Image.fromarray(np.clip(diff_array + 128, 0, 255).astype(np.uint8))
    diff_img.save("debug_difference_image.bmp")
    
    # Flatten the difference array
    diff_values = diff_array.flatten().tolist()
    
    # Clip difference values to -128 to 127 range
    diff_values = [max(-128, min(127, x)) for x in diff_values]
    
    # Calculate entropy of original image
    original_entropy = calculate_entropy(img_array.flatten().tolist())
    print(f"Original image entropy: {original_entropy:.4f} bits/pixel")
    
    # Calculate entropy of difference image
    diff_entropy = calculate_entropy(diff_values)
    print(f"Difference image entropy: {diff_entropy:.4f} bits/pixel")
    
    # Compress the difference values
    compressed_codes = compress_lzw(diff_values)
    
    # Calculate average code length
    code_length = 12  # Standard LZW code length
    avg_code_length = (len(compressed_codes) * code_length) / len(diff_values)
    print(f"Average code length: {avg_code_length:.4f} bits/pixel")
    
    # Save compressed data and image dimensions
    compressed_file_path = os.path.splitext(image_path)[0] + "_diff_compressed.lzw"
    with open(compressed_file_path, 'wb') as f:
        # Write image dimensions
        f.write(width.to_bytes(2, byteorder='big'))
        f.write(height.to_bytes(2, byteorder='big'))
        
        # Write the number of compressed codes
        f.write(len(compressed_codes).to_bytes(4, byteorder='big'))
        
        # Write compressed data
        for code in compressed_codes:
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