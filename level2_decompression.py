import os
import numpy as np
from PIL import Image
import image_tools

def decompress_lzw(compressed_data):
    """LZW decompression algorithm with improved error handling"""
    if not compressed_data:
        return []
    
    # Initialize dictionary
    dictionary = {i: [i] for i in range(256)}
    next_code = 256
    
    # Get the first code and decode
    current = compressed_data[0]
    if current >= 256:
        print(f"Warning: First code {current} >= 256, setting to 0")
        current = 0
    
    result = [current]
    
    # Process remaining codes
    for code in compressed_data[1:]:
        # Check if code exists in dictionary
        if code in dictionary:
            entry = dictionary[code].copy()
        elif code == next_code:
            # Special case: code not yet in dictionary
            entry = dictionary[current].copy()
            if entry:
                entry.append(entry[0])
            else:
                entry = [0]  # Fallback if entry is empty
        else:
            # Invalid code - skip and continue
            print(f"Warning: Code {code} not in dictionary and not next code {next_code}")
            # Try to recover by using a valid code
            if current in dictionary:
                entry = dictionary[current].copy()
                if entry:
                    entry.append(entry[0])
                else:
                    entry = [0]
            else:
                entry = [0]  # Last resort fallback
        
        # Add to result
        result.extend(entry)
        
        # Add to dictionary
        if next_code < 65536:  # 16-bit limit
            new_entry = dictionary[current].copy()
            if len(entry) > 0:
                new_entry.append(entry[0])
                dictionary[next_code] = new_entry
                next_code += 1
        
        current = code
    
    return result

def try_decompress_with_different_sizes(compressed_file_path):
    """Try decompressing with different byte sizes for dimensions"""
    # Try combinations of width and height byte sizes
    possible_sizes = [(4, 4), (2, 2), (4, 2), (2, 4)]
    
    for width_bytes, height_bytes in possible_sizes:
        try:
            with open(compressed_file_path, 'rb') as f:
                # Read dimensions with the current byte size
                width = int.from_bytes(f.read(width_bytes), byteorder='big')
                height = int.from_bytes(f.read(height_bytes), byteorder='big')
                
                # Check if dimensions look reasonable
                if 0 < width <= 10000 and 0 < height <= 10000:
                    print(f"Trying dimensions: {width}x{height} (width bytes: {width_bytes}, height bytes: {height_bytes})")
                    
                    # Read compressed data
                    compressed_data = []
                    chunk = f.read(2)  # Read 2 bytes (16-bit)
                    while chunk:
                        if len(chunk) == 2:  # Ensure we read exactly 2 bytes
                            value = int.from_bytes(chunk, byteorder='big')
                            compressed_data.append(value)
                        chunk = f.read(2)
                    
                    # Decompress and check if successful
                    decompressed_pixels = decompress_lzw(compressed_data)
                    
                    # If decompressed pixels count is close to expected, this might be the right size
                    expected_pixels = width * height
                    if abs(len(decompressed_pixels) - expected_pixels) < expected_pixels * 0.1:  # Within 10% of expected
                        return width, height, compressed_data
                    
        except Exception as e:
            print(f"Error with width_bytes={width_bytes}, height_bytes={height_bytes}: {e}")
    
    # If all attempts fail, raise an exception
    raise ValueError("Could not determine correct image dimensions from compressed file")

def decompress_image_file(compressed_file_path):
    """Decompress compressed image file with improved error handling"""
    try:
        # Try to determine correct dimensions
        try:
            width, height, compressed_data = try_decompress_with_different_sizes(compressed_file_path)
        except ValueError:
            # Fallback to standard 4-byte reading
            with open(compressed_file_path, 'rb') as f:
                # Read dimensions
                width = int.from_bytes(f.read(4), byteorder='big')
                height = int.from_bytes(f.read(4), byteorder='big')
                
                # Read compressed data
                compressed_data = []
                chunk = f.read(2)  # Read 2 bytes (16-bit)
                while chunk:
                    if len(chunk) == 2:  # Ensure we read exactly 2 bytes
                        value = int.from_bytes(chunk, byteorder='big')
                        compressed_data.append(value)
                    chunk = f.read(2)
        
        print(f"Decompressing: {width}x{height} image")
        print(f"Number of compressed codes read: {len(compressed_data)}")
        
        # Decompress the data
        decompressed_pixels = decompress_lzw(compressed_data)
        
        # Ensure we have the correct number of pixels
        expected_pixels = width * height
        if len(decompressed_pixels) > expected_pixels:
            print(f"Warning: Got {len(decompressed_pixels)} pixels, truncating to {expected_pixels}")
            decompressed_pixels = decompressed_pixels[:expected_pixels]
        elif len(decompressed_pixels) < expected_pixels:
            print(f"Warning: Got only {len(decompressed_pixels)} pixels, expected {expected_pixels}")
            padding = [0] * (expected_pixels - len(decompressed_pixels))
            decompressed_pixels.extend(padding)
        
        # Reshape to 2D array
        img_array = np.array(decompressed_pixels, dtype=np.uint8).reshape((height, width))
        
        # Save the restored image using PIL
        restored_img = image_tools.np2PIL(img_array)
        restored_file_path = os.path.splitext(compressed_file_path)[0] + "_restored.bmp"
        restored_img.save(restored_file_path)
        
        # Compare with original if available (optional)
        verify_decompression(compressed_file_path, restored_img)
        
        print(f"Image decompressed and saved as {restored_file_path}")
        return restored_file_path
    
    except Exception as e:
        print(f"Image decompression error: {e}")
        import traceback
        traceback.print_exc()  # Print detailed error information
        return None

def verify_decompression(compressed_file_path, restored_img):
    """Verify decompression by comparing with original (if available)"""
    try:
        # Try different possible original file paths
        possible_paths = [
            os.path.splitext(compressed_file_path)[0].replace("_compressed", "") + ".bmp",
            os.path.splitext(compressed_file_path)[0].replace("_grayscale_compressed", "") + ".bmp",
            os.path.splitext(compressed_file_path)[0] + ".bmp"
        ]
        
        for original_path in possible_paths:
            if os.path.exists(original_path):
                original_img = image_tools.readPILimg(original_path)
                
                # Convert original image to grayscale if it's not already
                if original_img.mode != "L":
                    original_img = image_tools.color2gray(original_img)
                
                # Resize if dimensions don't match
                if original_img.size != restored_img.size:
                    print(f"Warning: Original size {original_img.size} doesn't match restored size {restored_img.size}")
                    original_img = original_img.resize(restored_img.size)
                
                original_array = image_tools.PIL2np(original_img)
                restored_array = image_tools.PIL2np(restored_img)
                
                if np.array_equal(original_array, restored_array):
                    print(f"Decompression successful! Original and restored images are identical.")
                    return True
                else:
                    print(f"Decompression completed, but images differ.")
                    # Calculate the percentage of different pixels
                    diff = np.sum(original_array != restored_array)
                    total = original_array.size
                    print(f"Different pixels: {diff}/{total} ({diff/total*100:.2f}%)")
                    return False
                
        print("Original image not found for comparison.")
        return False
    except Exception as e:
        print(f"Error during verification: {e}")
        return False

def main():
    # Decompress the image file
    compressed_file_path = "small_image_grayscale_compressed.lzw"
    print(f"Trying to decompress: {compressed_file_path}")
    
    # Check if file exists
    if not os.path.exists(compressed_file_path):
        print(f"Error: File {compressed_file_path} not found!")
        return
    
    # Try to decompress
    result = decompress_image_file(compressed_file_path)
    
    if result:
        print(f"Decompression completed: {result}")
    else:
        print("Decompression failed.")

if __name__ == "__main__":
    main() 