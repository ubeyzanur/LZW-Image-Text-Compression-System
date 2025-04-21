import os
import numpy as np
from PIL import Image
import image_tools

def restore_from_difference_image(diff_array):
    """Restore the original image from the difference image."""
    height, width = diff_array.shape
    restored_array = diff_array.copy().astype(np.int16)  # Ensure int16 type
    
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
    """Decompress a list of codes using LZW algorithm."""
    # Ensure compressed data is not empty
    if not compressed:
        return []
    
    # Build the dictionary with single values
    dict_size = 256
    dictionary = {}
    for i in range(-128, 128):
        dictionary[i + 128] = [i]  # Map 0-255 to -128 to 127
    
    # Get the first code
    first_code = compressed[0]
    if first_code >= dict_size:
        raise ValueError(f"Invalid first code: {first_code}. Dictionary only has {dict_size} entries.")
    
    w = dictionary[first_code]
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
    compressed_file_path = "big_image_diff_compressed.lzw"
    
    with open(compressed_file_path, 'rb') as f:
        # Read image dimensions
        width = int.from_bytes(f.read(2), byteorder='big')
        height = int.from_bytes(f.read(2), byteorder='big')
        
        # Read the number of compressed codes
        code_count = int.from_bytes(f.read(4), byteorder='big')
        
        # Read compressed data
        compressed_data = []
        for _ in range(code_count):
            code = int.from_bytes(f.read(2), byteorder='big')
            compressed_data.append(code)
    
    print(f"Decompressing image with dimensions: {width}x{height}")
    print(f"Number of compressed codes: {len(compressed_data)}")
    print(f"First few codes: {compressed_data[:10]}")
    
    try:
        # Decompress to get difference values
        decompressed_diff_values = decompress_lzw(compressed_data)
        
        # Ensure we have the correct number of pixels
        expected_pixels = width * height
        if len(decompressed_diff_values) > expected_pixels:
            print(f"Warning: Got {len(decompressed_diff_values)} pixels, expected {expected_pixels}")
            decompressed_diff_values = decompressed_diff_values[:expected_pixels]
        elif len(decompressed_diff_values) < expected_pixels:
            print(f"Warning: Got only {len(decompressed_diff_values)} pixels, expected {expected_pixels}")
            decompressed_diff_values.extend([0] * (expected_pixels - len(decompressed_diff_values)))
        
        # Reshape to 2D array
        diff_array = np.array(decompressed_diff_values, dtype=np.int16).reshape((height, width))
        
        # Save the difference image for debugging
        diff_img = Image.fromarray(np.clip(diff_array + 128, 0, 255).astype(np.uint8))
        diff_img.save("debug_decompressed_difference.bmp")
        
        # Restore original image from differences
        restored_array = restore_from_difference_image(diff_array)
        
        # Convert to PIL Image
        restored_img = image_tools.np2PIL(restored_array)
        
        # Save the restored image
        image_path = "big_image.bmp"
        restored_file_path = os.path.splitext(image_path)[0] + "_diff_restored.bmp"
        restored_img.save(restored_file_path)
        
        # Compare original and restored images
        original_img = image_tools.readPILimg(image_path)
        if original_img.mode != "L":
            original_img = image_tools.color2gray(original_img)
        original_array = image_tools.PIL2np(original_img)
        
        if np.array_equal(original_array, restored_array):
            print("Decompression successful! Original and restored images are identical.")
        else:
            print("Decompression failed! Original and restored images are different.")
            # Calculate the percentage of different pixels
            diff = np.sum(original_array != restored_array)
            total = original_array.size
            print(f"Different pixels: {diff}/{total} ({diff/total*100:.2f}%)")
        
        print(f"Image decompressed and saved as {restored_file_path}")
    except Exception as e:
        print(f"Error during decompression: {e}")
        # Daha fazla hata ayıklama bilgisi
        if compressed_data:
            print(f"Min code: {min(compressed_data)}, Max code: {max(compressed_data)}")

if __name__ == "__main__":
    main() 