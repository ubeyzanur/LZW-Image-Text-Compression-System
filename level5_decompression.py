import os
import numpy as np
from PIL import Image
import image_tools

def restore_from_difference_image(diff_array):
    """Restore the original image from the difference image."""
    height, width = diff_array.shape
    restored_array = diff_array.copy()
    
    # Restore the first column (starting from the second pixel)
    for i in range(1, height):
        restored_array[i, 0] = int(restored_array[i, 0]) + int(restored_array[i-1, 0])
    
    # Restore each row (starting from the second pixel)
    for i in range(height):
        for j in range(1, width):
            restored_array[i, j] = int(restored_array[i, j]) + int(restored_array[i, j-1])
    
    # Ensure values are within 0-255 range
    restored_array = np.clip(restored_array, 0, 255).astype(np.uint8)
    
    return restored_array

def decompress_lzw(compressed):
    """Decompress a list of codes using LZW algorithm with integer values."""
    # Ensure compressed data is not empty
    if not compressed:
        return []
    
    # Build the dictionary with single values
    dict_size = 256
    dictionary = {}
    for i in range(dict_size):
        dictionary[i] = [i - 128]  # Map from 0-255 range back to -128 to 127
    
    # Get the first code
    w = dictionary[compressed[0]]
    result = w.copy()
    
    for k in compressed[1:]:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + [w[0]]
        else:
            raise ValueError(f"Bad compressed code: {k}")
        
        # Add entry to result
        result.extend(entry)
        
        # Add to dictionary if we haven't exceeded the limit
        if dict_size < 4096:  # Limit dictionary size to 12-bit codes
            dictionary[dict_size] = w + [entry[0]]
            dict_size += 1
        
        w = entry
    
    return result

def main():
    # Read the compressed file
    compressed_file_path = "small_image_color_diff_compressed.lzw"
    
    with open(compressed_file_path, 'rb') as f:
        # Read image dimensions
        width = int.from_bytes(f.read(2), byteorder='big')
        height = int.from_bytes(f.read(2), byteorder='big')
        
        # Read the length of each compressed channel
        r_length = int.from_bytes(f.read(4), byteorder='big')
        g_length = int.from_bytes(f.read(4), byteorder='big')
        b_length = int.from_bytes(f.read(4), byteorder='big')
        
        # Read compressed data for each channel
        r_compressed = []
        for _ in range(r_length):
            code = int.from_bytes(f.read(2), byteorder='big')
            r_compressed.append(code)
        
        g_compressed = []
        for _ in range(g_length):
            code = int.from_bytes(f.read(2), byteorder='big')
            g_compressed.append(code)
        
        b_compressed = []
        for _ in range(b_length):
            code = int.from_bytes(f.read(2), byteorder='big')
            b_compressed.append(code)
    
    print(f"Decompressing color difference image with dimensions: {width}x{height}")
    
    # Decompress each channel
    r_decompressed = decompress_lzw(r_compressed)
    g_decompressed = decompress_lzw(g_compressed)
    b_decompressed = decompress_lzw(b_compressed)
    
    # Ensure we have the correct number of pixels for each channel
    expected_pixels = width * height
    
    # Truncate or pad the decompressed data if necessary
    if len(r_decompressed) > expected_pixels:
        r_decompressed = r_decompressed[:expected_pixels]
    elif len(r_decompressed) < expected_pixels:
        print(f"Warning: Red channel has only {len(r_decompressed)} pixels, expected {expected_pixels}")
        r_decompressed.extend([0] * (expected_pixels - len(r_decompressed)))
    
    if len(g_decompressed) > expected_pixels:
        g_decompressed = g_decompressed[:expected_pixels]
    elif len(g_decompressed) < expected_pixels:
        print(f"Warning: Green channel has only {len(g_decompressed)} pixels, expected {expected_pixels}")
        g_decompressed.extend([0] * (expected_pixels - len(g_decompressed)))
    
    if len(b_decompressed) > expected_pixels:
        b_decompressed = b_decompressed[:expected_pixels]
    elif len(b_decompressed) < expected_pixels:
        print(f"Warning: Blue channel has only {len(b_decompressed)} pixels, expected {expected_pixels}")
        b_decompressed.extend([0] * (expected_pixels - len(b_decompressed)))
    
    # Reshape to 2D arrays
    r_diff_array = np.array(r_decompressed, dtype=np.int16).reshape((height, width))
    g_diff_array = np.array(g_decompressed, dtype=np.int16).reshape((height, width))
    b_diff_array = np.array(b_decompressed, dtype=np.int16).reshape((height, width))
    
    # Restore original channels from differences
    r_restored = restore_from_difference_image(r_diff_array)
    g_restored = restore_from_difference_image(g_diff_array)
    b_restored = restore_from_difference_image(b_diff_array)
    
    # Stack the channels to create a 3D array
    rgb_array = np.stack((r_restored, g_restored, b_restored), axis=2)
    
    # Convert to PIL Image
    restored_img = image_tools.np2PIL(rgb_array)
    
    # Save the restored image
    image_path = "small_image.bmp"
    restored_file_path = os.path.splitext(image_path)[0] + "_color_diff_restored.bmp"
    restored_img.save(restored_file_path)
    
    # Compare original and restored images
    original_img = image_tools.readPILimg(image_path)
    if original_img.mode != "RGB":
        original_img = original_img.convert("RGB")
    original_array = image_tools.PIL2np(original_img)
    
    if np.array_equal(original_array, rgb_array):
        print("Decompression successful! Original and restored images are identical.")
    else:
        print("Decompression completed, but original and restored images are different.")
        # Calculate the percentage of different pixels
        diff = np.sum(original_array != rgb_array)
        total = original_array.size
        print(f"Different pixels: {diff}/{total} ({diff/total*100:.2f}%)")
    
    print(f"Image decompressed and saved as {restored_file_path}")

if __name__ == "__main__":
    main() 