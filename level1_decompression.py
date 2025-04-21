import os

def decompress(compressed):
    """Decompress a list of output ks to a string."""
    from io import StringIO
    # Build the dictionary.
    dict_size = 256
    dictionary = {i: chr(i) for i in range(dict_size)}
    # use StringIO, otherwise this becomes O(N^2)
    # due to string concatenation in a loop
    result = StringIO()
    
    if not compressed:
        return ""
        
    w = chr(compressed.pop(0))
    result.write(w)
    
    for k in compressed:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0]
        else:
            # Daha güvenli bir yaklaşım - hata fırlatmak yerine atla
            print(f'Warning: Bad compressed code: {k}, skipping')
            continue
            
        result.write(entry)
        
        if dict_size < 65536:  # 2^16 sınırlaması
            # Add w+entry[0] to the dictionary.
            dictionary[dict_size] = w + entry[0]
            dict_size += 1
            
        w = entry
        
    return result.getvalue()

def remove_padding(padded_encoded_text, code_length):
    """Remove padding from the encoded text and convert to integer codes."""
    if len(padded_encoded_text) < 8:
        print("Warning: Padded text too short")
        return []
        
    padded_info = padded_encoded_text[:8]
    try:
        extra_padding = int(padded_info, 2)
    except ValueError:
        print(f"Warning: Invalid padding info: {padded_info}")
        extra_padding = 0
        
    padded_encoded_text = padded_encoded_text[8:]
    
    if extra_padding > len(padded_encoded_text):
        print(f"Warning: Invalid padding value: {extra_padding} > {len(padded_encoded_text)}")
        extra_padding = 0
        
    encoded_text = padded_encoded_text[:-1 * extra_padding] if extra_padding > 0 else padded_encoded_text
    
    int_codes = []
    for bits in range(0, len(encoded_text), code_length):
        if bits + code_length <= len(encoded_text):
            try:
                code = int(encoded_text[bits:bits+code_length], 2)
                int_codes.append(code)
            except ValueError:
                print(f"Warning: Invalid bit sequence: {encoded_text[bits:bits+code_length]}")
                
    return int_codes

def decompress_text_file(compressed_file_path):
    """Decompress a text file compressed with LZW"""
    # Determine code length
    # Try different code lengths to see which one works best
    for code_length in [12, 10, 14, 16]:
        try:
            # Read the compressed file
            with open(compressed_file_path, 'rb') as file:
                byte_array = file.read()
            
            # Convert byte array to binary string
            bit_string = ""
            for byte in byte_array:
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
            
            # Remove padding
            int_codes = remove_padding(bit_string, code_length)
            
            # Skip if no codes were extracted
            if not int_codes:
                print(f"No valid codes found with code_length={code_length}, trying another")
                continue
                
            # Decompress
            decompressed_text = decompress(int_codes.copy())
            
            # Save the decompressed text
            filename, file_extension = os.path.splitext(compressed_file_path)
            decompressed_file_path = filename.replace("_compressed", "_decompressed") + ".txt"
            
            with open(decompressed_file_path, 'w', encoding='utf-8') as file:
                file.write(decompressed_text)
            
            print(f"Successfully decompressed with code_length={code_length}")
            return decompressed_file_path
            
        except Exception as e:
            print(f"Failed with code_length={code_length}: {e}")
    
    # If we get here, all attempts failed
    print("All decompression attempts failed")
    return None

def main():
    # Decompress the compressed file
    compressed_file_path = "long_text_compressed.bin"
    print("Decompressing compressed file...")
    decompressed_file = decompress_text_file(compressed_file_path)
    
    if decompressed_file:
        print(f"Compressed file decompressed and saved as {decompressed_file}")
    else:
        print("Decompression failed")

if __name__ == "__main__":
    main() 