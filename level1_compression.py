import os
import math

def compress(uncompressed):
    """Compress a string to a list of output symbols."""
    # Build the dictionary.
    dict_size = 256
    dictionary = {chr(i): i for i in range(dict_size)}
    w = ""
    result = []
    for c in uncompressed:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            # Add wc to the dictionary.
            dictionary[wc] = dict_size
            dict_size += 1
            w = c
    # Output the code for w.
    if w:
        result.append(dictionary[w])
    return result

def int_array_to_binary_string(int_array, code_length):
    """Convert integer array to binary string using code_length bits for each integer."""
    bitstr = ""
    bits = code_length
    for num in int_array:
        for n in range(bits):
            if num & (1 << (bits - 1 - n)):
                bitstr += "1"
            else:
                bitstr += "0"
    return bitstr

def pad_encoded_text(encoded_text):
    """Add padding to make the length of encoded_text a multiple of 8."""
    extra_padding = 8 - len(encoded_text) % 8
    for i in range(extra_padding):
        encoded_text += "0"
    padded_info = "{0:08b}".format(extra_padding)
    encoded_text = padded_info + encoded_text
    return encoded_text

def get_byte_array(padded_encoded_text):
    """Convert padded binary string to byte array."""
    if (len(padded_encoded_text) % 8 != 0):
        print("Encoded text not padded properly")
        exit(0)
    b = bytearray()
    for i in range(0, len(padded_encoded_text), 8):
        byte = padded_encoded_text[i:i + 8]
        b.append(int(byte, 2))
    return b

def compress_text(file_path, code_length=12):
    """Compress the text file and save the compressed file."""
    # Read the text file
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    print(f"Original text length: {len(text)} characters")
    
    # Compress the text
    compressed_codes = compress(text)
    
    print(f"Number of compressed codes: {len(compressed_codes)}")
    
    # Convert to binary string
    binary_string = int_array_to_binary_string(compressed_codes, code_length)
    
    # Pad the binary string
    padded_binary_string = pad_encoded_text(binary_string)
    
    # Convert to byte array
    byte_array = get_byte_array(padded_binary_string)
    
    # Save the compressed file
    filename, file_extension = os.path.splitext(file_path)
    compressed_file_path = filename + "_compressed.bin"
    with open(compressed_file_path, 'wb') as file:
        file.write(byte_array)
    
    # Calculate compression ratio
    original_size = os.path.getsize(file_path)
    compressed_size = os.path.getsize(compressed_file_path)
    compression_ratio = compressed_size / original_size
    compression_factor = original_size / compressed_size
    space_saving = 1 - compression_ratio
    
    print(f"Original file size: {original_size} bytes")
    print(f"Compressed file size: {compressed_size} bytes")
    print(f"Compression Ratio (CR): {compression_ratio:.4f}")
    print(f"Compression Factor (CF): {compression_factor:.4f}")
    print(f"Space Saving (SS): {space_saving:.4f} ({space_saving*100:.2f}%)")
    
    return compressed_file_path

def compress_text_file(input_file_path):
    """Compress the text file using LZW compression for GUI compatibility"""
    print(f"GUI Compression Started: {input_file_path}")
    
    # Create .lzw file path for GUI compatibility
    output_file_path = os.path.splitext(input_file_path)[0] + "_compressed.lzw"
    
    try:
        # Read the text file
        with open(input_file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        print(f"File read, length: {len(text)} characters")
        
        # Compress the text using the existing compress function
        compressed_codes = compress(text)
        
        print(f"Compression completed, {len(compressed_codes)} codes")
        
        # Save the compressed data in .lzw format that GUI expects
        with open(output_file_path, 'wb') as file:
            # Save the original text length (4 bytes)
            file.write(len(text).to_bytes(4, byteorder='big'))
            
            # Save each code (4 bytes each)
            for code in compressed_codes:
                file.write(code.to_bytes(4, byteorder='big'))
        
        print(f"File successfully saved: {output_file_path}")
        
        # Calculate compression metrics
        original_size = os.path.getsize(input_file_path)
        compressed_size = os.path.getsize(output_file_path)
        print(f"Original size: {original_size} bytes")
        print(f"Compressed size: {compressed_size} bytes")
        
        return output_file_path
    
    except Exception as e:
        print(f"Compression error: {str(e)}")
        return None

def main():
    # Compress the text file
    file_path = "long_text.txt"
    print("Compressing text file...")
    compressed_file = compress_text(file_path)
    print(f"Text file compressed and saved as {compressed_file}")

if __name__ == "__main__":
    main() 