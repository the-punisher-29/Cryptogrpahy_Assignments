import os
import sys
from PIL import Image
import numpy as np
from collections import defaultdict
import random
import time

def analyze_edges(img_array):
    """Analyze image for edge continuity"""
    # Calculate horizontal and vertical differences
    h_diff = np.sum(np.abs(img_array[:, 1:] - img_array[:, :-1]))
    v_diff = np.sum(np.abs(img_array[1:, :] - img_array[:-1, :]))
    return h_diff, v_diff

def get_block_variance(img_array, block_size=8):
    """Calculate variance within blocks to identify coherent regions"""
    h, w, c = img_array.shape if len(img_array.shape) > 2 else (*img_array.shape, 1)
    variances = []
    
    for y in range(0, h, block_size):
        for x in range(0, w, block_size):
            if y+block_size <= h and x+block_size <= w:
                block = img_array[y:y+block_size, x:x+block_size]
                var = np.var(block)
                variances.append(var)
    
    return np.mean(variances)

def evaluate_permutation(images, permutation):
    """Evaluate a permutation by applying it to all images and measuring continuity"""
    total_score = 0
    for img in images:
        width, height = img.size
        pixels = list(img.getdata())
        
        # Apply inverse permutation (for decryption)
        inverse_perm = [-1] * len(permutation)
        for i, p in enumerate(permutation):
            if p < len(inverse_perm):
                inverse_perm[p] = i
        
        new_pixels = [pixels[inverse_perm[i]] if i < len(inverse_perm) and inverse_perm[i] < len(pixels) else pixels[i] 
                      for i in range(len(pixels))]
        
        # Convert to numpy array for analysis
        if img.mode == 'RGB':
            img_array = np.array(new_pixels).reshape(height, width, 3)
        elif img.mode == 'RGBA':
            img_array = np.array(new_pixels).reshape(height, width, 4)
        else:
            img_array = np.array(new_pixels).reshape(height, width)
        
        # Calculate edge score and block variance
        edge_score = sum(analyze_edges(img_array))
        variance_score = get_block_variance(img_array)
        
        # Lower edge score is better (fewer discontinuities)
        # Higher variance within blocks can indicate noise (worse)
        score = edge_score + variance_score
        total_score += score
    
    return total_score

def decrypt_image(img, permutation):
    """Apply a permutation to decrypt an image"""
    width, height = img.size
    pixels = list(img.getdata())
    
    # Create inverse permutation
    inverse_perm = [-1] * len(permutation)
    for i, p in enumerate(permutation):
        if p < len(inverse_perm):
            inverse_perm[p] = i
    
    # Apply inverse permutation
    new_pixels = [pixels[inverse_perm[i]] if i < len(inverse_perm) and inverse_perm[i] < len(pixels) else pixels[i] 
                  for i in range(len(pixels))]
    
    # Create new image
    new_img = Image.new(img.mode, img.size)
    new_img.putdata(new_pixels)
    return new_img

def greedy_search(images, max_iterations=1000, timeout=120):
    """Use greedy search to find a good permutation"""
    if not images:
        return None
    
    # Get dimensions
    img = images[0]
    width, height = img.size
    pixel_count = width * height
    
    # Start with identity permutation
    best_perm = list(range(pixel_count))
    best_score = evaluate_permutation(images, best_perm)
    
    print(f"Initial score: {best_score}")
    
    start_time = time.time()
    iterations_without_improvement = 0
    
    for iteration in range(max_iterations):
        if time.time() - start_time > timeout:
            print(f"Timeout after {iteration} iterations")
            break
            
        if iterations_without_improvement > 100:
            # Reset with some randomness to escape local minimum
            new_perm = best_perm.copy()
            for _ in range(pixel_count // 10):  # Swap 10% of positions
                i, j = random.sample(range(pixel_count), 2)
                new_perm[i], new_perm[j] = new_perm[j], new_perm[i]
            iterations_without_improvement = 0
        else:
            # Make a small change to current best permutation
            new_perm = best_perm.copy()
            
            # Strategy 1: Swap two random positions
            i, j = random.sample(range(pixel_count), 2)
            new_perm[i], new_perm[j] = new_perm[j], new_perm[i]
            
            # Strategy 2: Sometimes swap adjacent pixels (helps with locality)
            if random.random() < 0.3:
                x = random.randint(0, width-2)
                y = random.randint(0, height-1)
                i = y * width + x
                j = i + 1
                if i < pixel_count and j < pixel_count:
                    new_perm[i], new_perm[j] = new_perm[j], new_perm[i]
            
            # Strategy 3: Sometimes swap pixels in vertical pairs
            if random.random() < 0.3:
                x = random.randint(0, width-1)
                y = random.randint(0, height-2)
                i = y * width + x
                j = (y+1) * width + x
                if i < pixel_count and j < pixel_count:
                    new_perm[i], new_perm[j] = new_perm[j], new_perm[i]
        
        # Evaluate the new permutation
        new_score = evaluate_permutation(images, new_perm)
        
        # Update if better
        if new_score < best_score:
            best_score = new_score
            best_perm = new_perm
            iterations_without_improvement = 0
            print(f"Iteration {iteration}: New best score {best_score}")
        else:
            iterations_without_improvement += 1
    
    return best_perm

def block_swap_search(images, block_size=8, max_iterations=500, timeout=120):
    """Search for good permutation by swapping blocks of pixels"""
    if not images:
        return None
    
    # Get dimensions
    img = images[0]
    width, height = img.size
    pixel_count = width * height
    
    # Calculate blocks
    blocks_w = width // block_size
    blocks_h = height // block_size
    
    # Start with identity permutation
    best_perm = list(range(pixel_count))
    best_score = evaluate_permutation(images, best_perm)
    
    print(f"Initial block search score: {best_score}")
    
    start_time = time.time()
    
    for iteration in range(max_iterations):
        if time.time() - start_time > timeout:
            print(f"Timeout after {iteration} block iterations")
            break
        
        # Create a copy of the current best permutation
        new_perm = best_perm.copy()
        
        # Randomly select two blocks to swap
        block1_x = random.randint(0, blocks_w-1)
        block1_y = random.randint(0, blocks_h-1)
        block2_x = random.randint(0, blocks_w-1)
        block2_y = random.randint(0, blocks_h-1)
        
        # Swap all pixels in the two blocks
        for y_offset in range(block_size):
            for x_offset in range(block_size):
                # Calculate pixel positions in first block
                y1 = block1_y * block_size + y_offset
                x1 = block1_x * block_size + x_offset
                if y1 < height and x1 < width:
                    idx1 = y1 * width + x1
                    
                    # Calculate pixel positions in second block
                    y2 = block2_y * block_size + y_offset
                    x2 = block2_x * block_size + x_offset
                    if y2 < height and x2 < width:
                        idx2 = y2 * width + x2
                        
                        # Swap in the permutation
                        if idx1 < pixel_count and idx2 < pixel_count:
                            new_perm[idx1], new_perm[idx2] = new_perm[idx2], new_perm[idx1]
        
        # Evaluate the new permutation
        new_score = evaluate_permutation(images, new_perm)
        
        # Update if better
        if new_score < best_score:
            best_score = new_score
            best_perm = new_perm
            print(f"Block iteration {iteration}: New best score {best_score}")
    
    return best_perm

def similarity_analysis(images, sample_size=1000):
    """Analyze similarity patterns across multiple images to infer permutation"""
    if len(images) < 2:
        return None
    
    # Get dimensions
    img = images[0]
    width, height = img.size
    pixel_count = width * height
    
    # Start with identity permutation
    perm = list(range(pixel_count))
    
    # Sample some pixel positions to compare across images
    sample_positions = random.sample(range(pixel_count), min(sample_size, pixel_count))
    
    # For each sampled position, find potential matches in other images
    position_candidates = defaultdict(list)
    
    for pos in sample_positions:
        # Get the pixel value at this position in each image
        values = []
        for img in images:
            pixels = list(img.getdata())
            values.append(pixels[pos])
        
        # For each image, find positions with similar values
        for img_idx, img in enumerate(images):
            pixels = list(img.getdata())
            target_value = values[img_idx]
            
            # Find similar pixels
            similar_positions = []
            for i in range(pixel_count):
                if i != pos and pixels[i] == target_value:
                    similar_positions.append(i)
            
            # Add to candidates
            if similar_positions:
                # Limit to a reasonable number of candidates
                position_candidates[pos].extend(similar_positions[:10])
    
    # Use these candidates to improve our permutation
    for original_pos, candidates in position_candidates.items():
        if candidates:
            # For simplicity, use the first candidate
            perm[original_pos] = candidates[0]
    
    return perm

def quick_pattern_detection(encrypted_images, timeout=30):
    """Faster version of pattern detection across images"""
    print("Starting quick pattern detection...")
    
    # Load images
    images = []
    for path in encrypted_images:
        img = Image.open(path)
        images.append(img)
    
    # Get dimensions
    width, height = images[0].size
    pixel_count = width * height
    
    # Approach 1: Greedy search
    print("Starting greedy search...")
    greedy_perm = greedy_search(images, max_iterations=200, timeout=timeout)
    
    # Approach 2: Block-based search
    print("Starting block-based search...")
    block_perm = block_swap_search(images, block_size=8, max_iterations=100, timeout=timeout)
    
    # Approach 3: Similarity analysis
    print("Starting similarity analysis...")
    similarity_perm = similarity_analysis(images)
    
    # Evaluate all approaches
    perms = [p for p in [greedy_perm, block_perm, similarity_perm] if p is not None]
    best_perm = None
    best_score = float('inf')
    
    for perm in perms:
        score = evaluate_permutation(images, perm)
        if score < best_score:
            best_score = score
            best_perm = perm
    
    return best_perm

def extract_text_from_images(image_paths):
    """Extract text from recovered images"""
    # Sort files by number in filename
    sorted_paths = sorted(image_paths, key=lambda path: 
                         int(''.join(filter(str.isdigit, os.path.basename(path)))) 
                         if any(c.isdigit() for c in os.path.basename(path)) else 0)
    
    # This will need to be customized based on how the characters are encoded in the images
    # For now, we'll use a simplified approach
    result = ""
    for path in sorted_paths:
        try:
            img = Image.open(path)
            # Analyze the image to extract the character
            # This is highly dependent on how the characters are encoded
            # For demonstration, let's extract the average color and convert to ASCII
            pixels = list(img.getdata())
            if img.mode in ('RGB', 'RGBA'):
                # For color images
                avg_r = sum(p[0] for p in pixels) / len(pixels)
                avg_g = sum(p[1] for p in pixels) / len(pixels)
                avg_b = sum(p[2] for p in pixels) / len(pixels)
                
                # Convert to character (this is a simplification)
                char_value = int((avg_r + avg_g + avg_b) / 3) % 128
                result += chr(char_value)
            else:
                # For grayscale
                avg = sum(pixels) / len(pixels)
                char_value = int(avg) % 128
                result += chr(char_value)
        except Exception as e:
            print(f"Error processing {path}: {e}")
    
    return result

def attempt_visual_decryption(image_path, output_path=None):
    """Try different approaches to decrypt an image and return the best result"""
    # Load image
    img = Image.open(image_path)
    width, height = img.size
    pixel_count = width * height
    
    # 1. Row-based reordering
    row_perm = []
    for y in range(height):
        row_start = y * width
        row_perm.extend(list(range(row_start, row_start + width)))
    
    # 2. Column-based reordering
    col_perm = []
    for x in range(width):
        for y in range(height):
            col_perm.append(y * width + x)
    
    # 3. Simple pattern-based (checkerboard)
    checkerboard_perm = []
    for i in range(pixel_count):
        y = i // width
        x = i % width
        if (x + y) % 2 == 0:
            # Even positions first
            new_pos = (y // 2) * width + (x // 2)
        else:
            # Odd positions next
            new_pos = (height // 2) * width + (y // 2) * width + (x // 2)
        # Ensure we don't exceed bounds
        if new_pos < pixel_count:
            checkerboard_perm.append(new_pos)
    
    # Ensure proper length
    while len(checkerboard_perm) < pixel_count:
        checkerboard_perm.append(len(checkerboard_perm))
    
    # Create a random permutation for testing
    random_perm = list(range(pixel_count))
    random.shuffle(random_perm)
    
    # Try each permutation
    perms = [row_perm, col_perm, checkerboard_perm, random_perm]
    best_img = None
    best_score = float('inf')
    
    for perm in perms:
        # Apply permutation
        decrypted = decrypt_image(img, perm)
        
        # Convert to array for analysis
        if img.mode == 'RGB':
            img_array = np.array(list(decrypted.getdata())).reshape(height, width, 3)
        elif img.mode == 'RGBA':
            img_array = np.array(list(decrypted.getdata())).reshape(height, width, 4)
        else:
            img_array = np.array(list(decrypted.getdata())).reshape(height, width)
        
        # Score the result
        h_diff, v_diff = analyze_edges(img_array)
        score = h_diff + v_diff
        
        if score < best_score:
            best_score = score
            best_img = decrypted
    
    # Save the best result if output path provided
    if output_path and best_img:
        best_img.save(output_path)
    
    return best_img

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
    
    encrypted_images.sort()  # Sort to ensure consistent order
    
    if not encrypted_images:
        print("No encrypted randomstring images found.")
        return
    
    print(f"Found {len(encrypted_images)} encrypted images.")
    
    # Create output directory
    output_dir = "recovered"
    os.makedirs(output_dir, exist_ok=True)
    
    # Try quick pattern detection first (with timeout)
    print("Attempting pattern detection across images...")
    pattern_perm = quick_pattern_detection(encrypted_images, timeout=30)
    
    recovered_images = []
    
    if pattern_perm:
        print("Using cross-image pattern analysis results...")
        pattern_dir = os.path.join(output_dir, "pattern_method")
        os.makedirs(pattern_dir, exist_ok=True)
        
        for img_path in encrypted_images:
            file_name = os.path.basename(img_path)
            output_path = os.path.join(pattern_dir, f"recovered_{file_name}")
            
            img = Image.open(img_path)
            decrypted = decrypt_image(img, pattern_perm)
            decrypted.save(output_path)
            recovered_images.append(output_path)
    
    # Fallback: Try visual decryption on each image
    print("Trying individual image decryption as fallback...")
    visual_dir = os.path.join(output_dir, "visual_method")
    os.makedirs(visual_dir, exist_ok=True)
    
    visual_recovered = []
    for img_path in encrypted_images:
        file_name = os.path.basename(img_path)
        output_path = os.path.join(visual_dir, f"recovered_{file_name}")
        
        decrypted = attempt_visual_decryption(img_path, output_path)
        visual_recovered.append(output_path)
    
    # Use the best method's results
    final_images = recovered_images if recovered_images else visual_recovered
    
    # Try to extract the random string
    random_string = extract_text_from_images(final_images)
    
    # Save the extracted string
    # Replace YOUR_SERIAL_NO with your actual serial number
    serial_no = "YOUR_SERIAL_NO"  # You should replace this with your actual serial number
    output_file = f"{serial_no}_randomstring2.txt"
    
    with open(output_file, "w") as f:
        f.write(random_string)
    
    print(f"Extracted random string: {random_string}")
    print(f"Saved to {output_file}")
    print("Note: You may need to manually inspect the recovered images and adjust the extraction method")

if __name__ == "__main__":
    main()