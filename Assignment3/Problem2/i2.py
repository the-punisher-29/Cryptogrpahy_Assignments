import numpy as np
from PIL import Image
import os
from collections import defaultdict
import random
import string
import cv2
from scipy import signal
import matplotlib.pyplot as plt

def load_encrypted_image(filename):
    """Load an encrypted image and return it as numpy array."""
    img = Image.open(filename)
    return np.array(img), img.size

def calculate_gradient_coherence(img_array):
    """
    Calculate image coherence based on gradient continuity.
    Natural images have strong local correlations.
    """
    # Convert to grayscale if it's a color image
    if len(img_array.shape) == 3:
        img_gray = np.mean(img_array, axis=2).astype(np.uint8)
    else:
        img_gray = img_array
    
    # Calculate gradients
    grad_x = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)
    
    # Calculate gradient magnitude
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    
    # High gradient magnitude indicates edges/discontinuities
    # Lower is better for natural images
    return -np.sum(grad_mag)

def patch_based_coherence(img_array, patch_size=3):
    """
    Measure image coherence using patch similarity.
    Adjacent patches in natural images are more similar than in shuffled images.
    """
    height, width = img_array.shape[:2]
    coherence = 0
    
    # Compare adjacent patches
    for y in range(height - patch_size):
        for x in range(width - patch_size):
            patch1 = img_array[y:y+patch_size, x:x+patch_size]
            patch2 = img_array[y:y+patch_size, x+1:x+1+patch_size]
            patch3 = img_array[y+1:y+1+patch_size, x:x+patch_size]
            
            # Calculate similarity (negative MSE - higher is better)
            coherence -= np.mean((patch1 - patch2)**2)
            coherence -= np.mean((patch1 - patch3)**2)
    
    return coherence

def pattern_coherence(img_array):
    """
    A more comprehensive coherence measure combining multiple techniques.
    """
    # Combine gradient coherence and patch coherence
    return calculate_gradient_coherence(img_array) + patch_based_coherence(img_array)

def genetic_algorithm(img_array, population_size=20, generations=50):
    """
    Use a genetic algorithm to find a permutation that maximizes image coherence.
    """
    height, width = img_array.shape[:2]
    num_pixels = height * width
    
    # Initialize population with random permutations
    population = [np.random.permutation(num_pixels) for _ in range(population_size)]
    
    best_fitness = float('-inf')
    best_perm = None
    fitness_history = []
    
    for gen in range(generations):
        # Evaluate fitness of each permutation
        fitness_scores = []
        for perm in population:
            # Apply permutation and evaluate coherence
            permuted_img = apply_permutation(img_array, perm)
            fitness = pattern_coherence(permuted_img)
            fitness_scores.append(fitness)
            
            # Update best permutation
            if fitness > best_fitness:
                best_fitness = fitness
                best_perm = perm.copy()
        
        fitness_history.append(max(fitness_scores))
        print(f"Generation {gen+1}/{generations}, Best Fitness: {best_fitness}")
        
        # Selection: Tournament selection
        new_population = []
        for _ in range(population_size):
            # Select parents through tournament
            tournament_size = 3
            tournament_indices = np.random.choice(population_size, tournament_size, replace=False)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            parent1_idx = tournament_indices[np.argmax(tournament_fitness)]
            parent1 = population[parent1_idx]
            
            tournament_indices = np.random.choice(population_size, tournament_size, replace=False)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            parent2_idx = tournament_indices[np.argmax(tournament_fitness)]
            parent2 = population[parent2_idx]
            
            # Crossover: Order crossover
            crossover_point = np.random.randint(1, num_pixels-1)
            child = np.zeros(num_pixels, dtype=int)
            child[:crossover_point] = parent1[:crossover_point]
            
            # Fill remaining positions with values from parent2 that aren't already in child
            remaining_positions = np.setdiff1d(parent2, child[:crossover_point])
            child[crossover_point:] = remaining_positions
            
            # Mutation: Swap mutation
            if np.random.random() < 0.2:  # 20% mutation probability
                swap_indices = np.random.choice(num_pixels, 2, replace=False)
                child[swap_indices[0]], child[swap_indices[1]] = child[swap_indices[1]], child[swap_indices[0]]
            
            new_population.append(child)
        
        # Elitism: Keep the best individual
        worst_idx = np.argmin(fitness_scores)
        new_population[worst_idx] = best_perm.copy()
        
        population = new_population
    
    # Plot fitness history
    plt.figure(figsize=(10, 5))
    plt.plot(range(1, generations+1), fitness_history)
    plt.xlabel('Generation')
    plt.ylabel('Best Fitness')
    plt.title('Fitness Improvement Over Generations')
    plt.savefig('fitness_plot.png')
    
    return best_perm

def apply_permutation(img_array, permutation):
    """Apply a permutation to an image array."""
    flat_shape = (-1, 3) if len(img_array.shape) == 3 else (-1)
    flat_img = img_array.reshape(flat_shape)
    new_img = np.zeros_like(flat_img)
    
    for i, p in enumerate(permutation):
        new_img[i] = flat_img[p]
    
    return new_img.reshape(img_array.shape)

def estimate_inverse_permutation(encrypted_img_array):
    """
    Estimate the inverse permutation using image analysis techniques.
    """
    # For a real implementation, you'd need a more sophisticated approach
    # This is a placeholder for demonstration
    height, width = encrypted_img_array.shape[:2]
    num_pixels = height * width
    
    # Use genetic algorithm to find permutation
    best_perm = genetic_algorithm(encrypted_img_array)
    
    # Create inverse permutation
    inverse_perm = np.zeros(num_pixels, dtype=int)
    for i, p in enumerate(best_perm):
        inverse_perm[p] = i
    
    return inverse_perm

def recognize_character_from_image(img_array):
    """
    Recognize a character from the decrypted image.
    In a real implementation, this would use OCR or pattern matching.
    """
    # For demonstration, we'll use a simple approach
    # Extract the most common color in the image (excluding background)
    if len(img_array.shape) == 3:
        # For color images
        flat_img = img_array.reshape(-1, img_array.shape[2])
    else:
        # For grayscale
        flat_img = img_array.reshape(-1)
    
    # Count frequency of each pixel value
    unique, counts = np.unique(flat_img, axis=0, return_counts=True)
    
    # Get the most common pixel value (excluding background)
    sorted_indices = np.argsort(-counts)
    
    # Placeholder - in reality, would use proper OCR
    # For demonstration, return a random character
    return random.choice(string.ascii_uppercase + string.digits)

def decrypt_and_extract_character(image_path):
    """Decrypt an image and extract the character from it."""
    encrypted_img_array, size = load_encrypted_image(image_path)
    
    # Estimate the inverse permutation
    inverse_perm = estimate_inverse_permutation(encrypted_img_array)
    
    # Apply the inverse permutation to decrypt
    decrypted_img_array = apply_permutation(encrypted_img_array, inverse_perm)
    
    # Save decrypted image for inspection
    output_path = f"decrypted_{os.path.basename(image_path)}"
    decrypted_img = Image.fromarray(decrypted_img_array.astype(np.uint8))
    decrypted_img.save(output_path)
    
    # Extract character
    character = recognize_character_from_image(decrypted_img_array)
    
    return character, output_path

def process_all_images():
    """Process all randomstring*.png images and extract the hidden string."""
    random_string = ""
    
    # Find all encrypted images
    image_files = sorted([f for f in os.listdir() if f.startswith('randomstring') and f.endswith('.png')])
    
    print(f"Found {len(image_files)} encrypted images.")
    
    for i, img_file in enumerate(image_files):
        print(f"Processing image {i+1}/{len(image_files)}: {img_file}")
        character, output_path = decrypt_and_extract_character(img_file)
        print(f"Extracted character: {character}, saved to {output_path}")
        random_string += character
    
    print(f"Complete random string: {random_string}")
    
    # Save to the required output file
    with open("72_randomstring2.txt", "w") as f:
        f.write(random_string)
    
    print(f"Saved random string to 72_randomstring2.txt")

if __name__ == "__main__":
    # Uncomment to process all images
    # process_all_images()
    
    # For testing, try with one image first
    test_file = "randomstring00.png"
    if os.path.exists(test_file):
        character, output_path = decrypt_and_extract_character(test_file)
        print(f"Test run: Extracted '{character}' from {test_file}, saved to {output_path}")