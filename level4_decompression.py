import os
import numpy as np
from PIL import Image
import image_tools

def decompress_lzw(compressed):
    """Decompress a list of codes using LZW algorithm."""
    if not compressed:
        return []
    
    # Build the dictionary with single values
    dict_size = 256
    dictionary = {i: chr(i) for i in range(dict_size)}
    
    # Get the first code
    w = dictionary[compressed[0]]
    result = [ord(w)]
    
    for k in compressed[1:]:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0]
        else:
            entry = w + w[0]  # Fallback for invalid codes
        
        # Add entry to result
        result.extend([ord(c) for c in entry])
        
        # Add to dictionary if we haven't exceeded the limit
        if dict_size < 4096:
            dictionary[dict_size] = w + entry[0]
            dict_size += 1
        
        w = entry
    
    return result

def read_compressed_file(compressed_file_path):
    """Read and parse the compressed file."""
    with open(compressed_file_path, 'rb') as f:
        # Read image dimensions
        width = int.from_bytes(f.read(4), byteorder='big')
        height = int.from_bytes(f.read(4), byteorder='big')
        
        # Read the length of each compressed channel
        r_length = int.from_bytes(f.read(4), byteorder='big')
        g_length = int.from_bytes(f.read(4), byteorder='big')
        b_length = int.from_bytes(f.read(4), byteorder='big')
        
        print(f"Reading image: {width}x{height}, channels: R={r_length}, G={g_length}, B={b_length}")
        
        # Read compressed data for each channel
        channels_compressed = []
        for length in [r_length, g_length, b_length]:
            channel = []
            for _ in range(length):
                code = int.from_bytes(f.read(2), byteorder='big')
                channel.append(code)
            channels_compressed.append(channel)
    
    return width, height, channels_compressed

def process_channel(compressed, width, height, channel_name=""):
    """Process a single compressed channel."""
    print(f"Decompressing {channel_name} channel...")
    decompressed = decompress_lzw(compressed)
    
    # Adjust to expected pixel count
    expected_pixels = width * height
    if len(decompressed) != expected_pixels:
        if len(decompressed) > expected_pixels:
            decompressed = decompressed[:expected_pixels]
        else:
            decompressed.extend([0] * (expected_pixels - len(decompressed)))
    
    return np.array(decompressed, dtype=np.uint8).reshape((height, width))

def decompress_image_file(compressed_file_path):
    """Decompress a color image file compressed with LZW"""
    try:
        # Read the compressed file
        width, height, channels_compressed = read_compressed_file(compressed_file_path)
        
        # Decompress each channel
        channel_names = ["red", "green", "blue"]
        channels = []
        
        for i, compressed in enumerate(channels_compressed):
            channel_array = process_channel(compressed, width, height, channel_names[i])
            channels.append(channel_array)
        
        # Stack the channels to create a 3D array
        rgb_array = np.stack(channels, axis=2)
        
        # Convert to PIL Image and save
        restored_img = image_tools.np2PIL(rgb_array)
        restored_file_path = os.path.splitext(compressed_file_path)[0] + "_restored.bmp"
        restored_img.save(restored_file_path)
        
        print(f"Image decompressed and saved as {restored_file_path}")
        return restored_file_path
        
    except Exception as e:
        print(f"Error decompressing image: {e}")
        return None

def compare_images(original_path, restored_path):
    """Compare original and restored images."""
    if not (os.path.exists(original_path) and os.path.exists(restored_path)):
        return False
    
    try:
        # Load images
        original_img = image_tools.readPILimg(original_path)
        restored_img = image_tools.readPILimg(restored_path)
        
        # Ensure both images are in RGB mode
        if original_img.mode != "RGB":
            original_img = original_img.convert("RGB")
        if restored_img.mode != "RGB":
            restored_img = restored_img.convert("RGB")
        
        # Check dimensions
        if original_img.size != restored_img.size:
            print("Images have different dimensions - cannot compare.")
            return False
        
        # Compare images
        original_array = image_tools.PIL2np(original_img)
        restored_array = image_tools.PIL2np(restored_img)
        
        if np.array_equal(original_array, restored_array):
            print("Images are identical!")
            return True
        else:
            diff = np.sum(original_array != restored_array)
            total = original_array.size
            print(f"Different pixels: {diff}/{total} ({diff/total*100:.2f}%)")
            return False
            
    except Exception as e:
        print(f"Error comparing images: {e}")
        return False

def main():
    compressed_file_path = "small_image_compressed.lzw"
    original_image_path = "small_image.bmp"
    
    restored_path = decompress_image_file(compressed_file_path)
    if restored_path:
        compare_images(original_image_path, restored_path)

if __name__ == "__main__":
    main() 