import os
import sys
from PIL import Image
import numpy as np
import random
import ast
import itertools

def decrypt_with_key(image_path, key_permutation, output_path=None):
    """Decrypt an image using a permutation key"""
    img = Image.open(image_path)
    width, height = img.size
    pixel_count = width * height
    
    # Ensure the key is the right length
    if len(key_permutation) != pixel_count:
        print(f"Warning: Key length ({len(key_permutation)}) doesn't match pixel count ({pixel_count})")
        # Truncate or extend key if necessary
        if len(key_permutation) > pixel_count:
            key_permutation = key_permutation[:pixel_count]
        else:
            key_permutation = key_permutation + list(range(len(key_permutation), pixel_count))
    
    # Create inverse permutation for decryption
    # This is the critical part - for each position in the original permutation,
    # we store the index where that position appeared
    inverse_perm = [0] * pixel_count
    for i, x in enumerate(key_permutation):
        if x < pixel_count:
            inverse_perm[x] = i
    
    # Apply the inverse permutation
    pixels = list(img.getdata())
    new_pixels = [0] * pixel_count
    
    for i, x in enumerate(inverse_perm):
        if i < pixel_count and x < len(pixels):
            new_pixels[i] = pixels[x]
    
    # Create new image
    new_img = Image.new(img.mode, img.size)
    new_img.putdata(new_pixels)
    
    if output_path:
        new_img.save(output_path)
    
    return new_img

def brute_force_small_permutation(encrypted_images, max_size=10):
    """Try all possible permutations for a small subset of pixels"""
    if not encrypted_images:
        return None
    
    # Load first image for reference
    img = Image.open(encrypted_images[0])
    width, height = img.size
    pixel_count = width * height
    
    print(f"Image dimensions: {width}x{height}, Total pixels: {pixel_count}")
    
    # For large images, we can't brute force the entire permutation
    # Instead, let's try to find a pattern by looking at a small subset
    subset_size = min(max_size, pixel_count)
    
    # Choose some positions to analyze
    positions = list(range(subset_size))
    
    # Try all permutations of these positions
    best_permutation = None
    best_score = float('inf')
    
    print(f"Trying permutations of {subset_size} positions...")
    for count, perm in enumerate(itertools.permutations(positions)):
        if count > 1000:  # Limit the number of permutations to try
            break
        
        # Create a full permutation using this subset
        full_perm = list(range(pixel_count))
        for i, p in enumerate(perm):
            full_perm[i] = p
        
        # Test this permutation on a small section of the image
        test_img = Image.open(encrypted_images[0])
        test_pixels = list(test_img.getdata())
        new_pixels = [0] * pixel_count
        
        # Apply just the subset permutation
        for i, p in enumerate(full_perm[:subset_size]):
            if p < pixel_count:
                new_pixels[i] = test_pixels[p]
        
        # Fill the rest with original values
        for i in range(subset_size, pixel_count):
            new_pixels[i] = test_pixels[i]
        
        # Create and analyze a test image
        test_new = Image.new(test_img.mode, test_img.size)
        test_new.putdata(new_pixels)
        
        # Convert to array for analysis
        if test_img.mode in ('RGB', 'RGBA'):
            channels = 3 if test_img.mode == 'RGB' else 4
            array = np.array(new_pixels[:subset_size*2]).reshape(-1, channels)
        else:
            array = np.array(new_pixels[:subset_size*2])
        
        # Simple scoring: look for smooth transitions
        if len(array.shape) > 1:
            score = np.sum(np.abs(array[1:] - array[:-1]))
        else:
            score = np.sum(np.abs(array[1:] - array[:-1]))
        
        if score < best_score:
            best_score = score
            best_permutation = list(perm)
            print(f"New best permutation found with score {score}: {best_permutation}")
    
    if best_permutation:
        # Try to infer a pattern from the best permutation
        pattern = find_pattern_in_permutation(best_permutation)
        if pattern:
            print(f"Detected pattern: {pattern}")
            # Extend the pattern to the full image
            full_pattern = extend_pattern(pattern, pixel_count)
            return full_pattern
    
    return None

def find_pattern_in_permutation(permutation):
    """Try to find a mathematical pattern in the permutation"""
    # Look for common patterns like: shift, reverse, etc.
    n = len(permutation)
    
    # Check if it's a shift
    shifts = [(permutation[i] - i) % n for i in range(n)]
    if all(shift == shifts[0] for shift in shifts):
        return {"type": "shift", "value": shifts[0]}
    
    # Check if it's a reverse
    if all(permutation[i] == n - 1 - i for i in range(n)):
        return {"type": "reverse"}
    
    # Check if it's a stride pattern
    for stride in range(2, min(n // 2, 10)):
        is_stride = True
        for i in range(n - stride):
            if i + stride < n and permutation[i+stride] - permutation[i] != stride:
                is_stride = False
                break
        if is_stride:
            return {"type": "stride", "value": stride}
    
    # Try to find a formula
    differences = [permutation[i+1] - permutation[i] for i in range(n-1)]
    if all(diff == differences[0] for diff in differences):
        return {"type": "linear", "slope": differences[0], "intercept": permutation[0]}
    
    return None

def extend_pattern(pattern, length):
    """Extend a detected pattern to cover the entire image"""
    result = list(range(length))
    
    if pattern["type"] == "shift":
        for i in range(length):
            result[i] = (i + pattern["value"]) % length
    
    elif pattern["type"] == "reverse":
        for i in range(length):
            result[i] = length - 1 - i
    
    elif pattern["type"] == "stride":
        stride = pattern["value"]
        for i in range(length):
            group = i // stride
            offset = i % stride
            result[i] = offset * (length // stride) + group
    
    elif pattern["type"] == "linear":
        for i in range(length):
            value = pattern["slope"] * i + pattern["intercept"]
            result[i] = int(value) % length
    
    return result

def try_common_permutations(encrypted_images):
    """Try common permutation types on the encrypted images"""
    if not encrypted_images:
        return None
    
    # Load first image for reference
    img = Image.open(encrypted_images[0])
    width, height = img.size
    pixel_count = width * height
    
    # Create test directory
    test_dir = "test_permutations"
    os.makedirs(test_dir, exist_ok=True)
    
    permutations = []
    
    # 1. Identity (no change)
    permutations.append(("identity", list(range(pixel_count))))
    
    # 2. Reverse
    reverse_perm = list(range(pixel_count))
    reverse_perm.reverse()
    permutations.append(("reverse", reverse_perm))
    
    # 3. Transpose (by row/column)
    transpose_perm = []
    for x in range(width):
        for y in range(height):
            transpose_perm.append(y * width + x)
    permutations.append(("transpose", transpose_perm))
    
    # 4. Row-based shuffling
    row_shuffle = []
    rows = list(range(height))
    random.shuffle(rows)
    for y in rows:
        row_shuffle.extend([y * width + x for x in range(width)])
    permutations.append(("row_shuffle", row_shuffle))
    
    # 5. Column-based shuffling
    col_shuffle = []
    cols = list(range(width))
    random.shuffle(cols)
    for x in cols:
        col_shuffle.extend([y * width + x for y in range(height)])
    permutations.append(("col_shuffle", col_shuffle))
    
    # 6. Interleaved rows
    interleaved_rows = []
    for i in range(height // 2):
        interleaved_rows.extend([i * width + x for x in range(width)])
        interleaved_rows.extend([(height - i - 1) * width + x for x in range(width)])
    # Add any remaining row if height is odd
    if height % 2 == 1:
        interleaved_rows.extend([(height // 2) * width + x for x in range(width)])
    permutations.append(("interleaved_rows", interleaved_rows))
    
    # 7. Block-based permutation (dividing the image into blocks)
    block_size = 8  # Try 8x8 blocks
    blocks_w = width // block_size
    blocks_h = height // block_size
    block_perm = []
    
    block_order = list(range(blocks_w * blocks_h))
    random.shuffle(block_order)
    
    for block_idx in block_order:
        block_y = block_idx // blocks_w
        block_x = block_idx % blocks_w
        
        for y_offset in range(block_size):
            for x_offset in range(block_size):
                y = block_y * block_size + y_offset
                x = block_x * block_size + x_offset
                if y < height and x < width:
                    block_perm.append(y * width + x)
    
    permutations.append(("block_shuffle", block_perm))
    
    # 8. XOR with position
    xor_perm = []
    for i in range(pixel_count):
        xor_perm.append(i ^ (i // width))
    permutations.append(("xor_position", xor_perm))
    
    # Try each permutation on the first image
    best_perm = None
    best_name = None
    best_score = float('inf')
    
    for name, perm in permutations:
        # Ensure permutation is valid
        perm = [p % pixel_count for p in perm]
        while len(perm) < pixel_count:
            perm.append(len(perm))
        
        output_path = os.path.join(test_dir, f"{name}_test.png")
        test_img = decrypt_with_key(encrypted_images[0], perm, output_path)
        
        # Score the result (very basic check for now)
        test_data = list(test_img.getdata())
        
        # Calculate simple edge score
        if img.mode in ('RGB', 'RGBA'):
            channels = 3 if img.mode == 'RGB' else 4
            array = np.array(test_data).reshape(height, width, channels)
            # Horizontal and vertical differences
            h_diff = np.sum(np.abs(array[:, 1:] - array[:, :-1]))
            v_diff = np.sum(np.abs(array[1:, :] - array[:-1, :]))
            score = h_diff + v_diff
        else:
            array = np.array(test_data).reshape(height, width)
            h_diff = np.sum(np.abs(array[:, 1:] - array[:, :-1]))
            v_diff = np.sum(np.abs(array[1:, :] - array[:-1, :]))
            score = h_diff + v_diff
        
        print(f"Permutation {name}: score {score}")
        
        if score < best_score:
            best_score = score
            best_perm = perm
            best_name = name
    
    print(f"Best permutation: {best_name} with score {best_score}")
    return best_perm

def try_otp_permutations(encrypted_images):
    """Try different approaches to recover the OTP permutation"""
    # First, try common permutation types
    common_perm = try_common_permutations(encrypted_images)
    
    # Then try to brute force a small section
    brute_perm = brute_force_small_permutation(encrypted_images)
    
    # Return the best permutation found
    return common_perm or brute_perm

def extract_text_from_images(image_paths):
    """Try to extract text from the recovered images"""
    # Sort by filename numbers
    sorted_paths = sorted(image_paths, key=lambda path: int(''.join(filter(str.isdigit, os.path.basename(path)))) if any(c.isdigit() for c in os.path.basename(path)) else 0)
    
    # Extract text by analyzing each image
    text = ""
    for path in sorted_paths:
        try:
            img = Image.open(path)
            # Convert to grayscale for simplicity
            if img.mode != 'L':
                img = img.convert('L')
            
            pixels = np.array(img)
            
            # Try different approaches to extract text:
            # 1. Check if it's a single character image
            if min(img.size) <= 64:  # Small image might be a character
                # Find the most common non-background pixel value
                values, counts = np.unique(pixels, return_counts=True)
                # Assume background is the most common value
                background = values[np.argmax(counts)]
                
                # Find the second most common value (likely the character)
                non_bg_indices = values != background
                if np.any(non_bg_indices):
                    non_bg_values = values[non_bg_indices]
                    non_bg_counts = counts[non_bg_indices]
                    if len(non_bg_values) > 0:
                        char_value = non_bg_values[np.argmax(non_bg_counts)]
                        # Check if the value is in ASCII range
                        if 32 <= char_value <= 126:
                            text += chr(char_value)
                        else:
                            # If not, try simple mapping
                            text += chr((char_value % 95) + 32)
            
            # 2. Try OCR-like approach for larger images
            else:
                # Threshold to find potential characters
                threshold = np.mean(pixels)
                binary = pixels > threshold
                
                # Count foreground pixels
                fg_count = np.sum(binary)
                
                # Estimate character based on foreground pixel count
                # (This is very simplistic - real OCR would be more complex)
                if fg_count > 0:
                    char_est = (fg_count % 95) + 32  # map to printable ASCII
                    text += chr(char_est)
        
        except Exception as e:
            print(f"Error processing {path}: {e}")
    
    # Check if the result looks like a reasonable string
    print(f"Extracted raw text: {text}")
    
    # Try to clean up the text (remove non-printable characters)
    cleaned_text = ''.join(c for c in text if 32 <= ord(c) <= 126)
    
    return cleaned_text

def main():
    # Check for encrypted images directory
    encrypted_dir = "encrypted"
    if not os.path.exists(encrypted_dir):
        print(f"Directory {encrypted_dir} not found.")
        return
    
    # Find all encrypted randomstring images
    encrypted_images = []
    for file in os.listdir(encrypted_dir):
        if file.startswith("randomstring") and file.endswith(".png"):
            encrypted_images.append(os.path.join(encrypted_dir, file))
    
    encrypted_images.sort()
    
    if not encrypted_images:
        print("No encrypted randomstring images found.")
        return
    
    print(f"Found {len(encrypted_images)} encrypted images: {[os.path.basename(p) for p in encrypted_images]}")
    
    # Create output directory
    output_dir = "recovered"
    os.makedirs(output_dir, exist_ok=True)
    
    # Try to recover the OTP permutation
    print("Trying to recover the OTP permutation...")
    perm = try_otp_permutations(encrypted_images)
    
    if not perm:
        print("Could not recover a permutation. Trying alternative methods...")
        # Try something else
        return
    
    # Use the recovered permutation to decrypt all images
    recovered_paths = []
    for i, img_path in enumerate(encrypted_images):
        file_name = os.path.basename(img_path)
        output_path = os.path.join(output_dir, f"recovered_{file_name}")
        
        print(f"Decrypting {file_name}...")
        decrypt_with_key(img_path, perm, output_path)
        recovered_paths.append(output_path)
    
    # Try to extract the random string from the recovered images
    print("Attempting to extract the random string...")
    random_string = extract_text_from_images(recovered_paths)
    
    # Save the extracted string
    # Replace YOUR_SERIAL_NO with your actual serial number
    serial_no = "YOUR_SERIAL_NO"
    output_file = f"{serial_no}_randomstring2.txt"
    
    with open(output_file, "w") as f:
        f.write(random_string)
    
    print(f"Extracted random string: {random_string}")
    print(f"Saved to {output_file}")
    print("Note: You may need to manually inspect the recovered images to verify the extraction")

if __name__ == "__main__":
    main()