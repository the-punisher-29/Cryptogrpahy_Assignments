import numpy as np
from PIL import Image
import os
import cv2
import pytesseract
# Explicitly set the path to Tesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
print(pytesseract.get_tesseract_version())  # Should print Tesseract version
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from collections import Counter
import string
import re

# Configure Tesseract path if needed
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows

# Directory containing encrypted images
ENCRYPTED_DIR = "encrypted"

def load_image(filepath):
    """Load image and return as numpy array."""
    img = Image.open(filepath)
    return np.array(img), img.size

def preprocess_for_ocr(img_array):
    """Preprocess image for better OCR results."""
    # Convert to grayscale if it's a color image
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array.copy()
    
    # Apply thresholding to get binary image
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Noise removal using morphological operations
    kernel = np.ones((2, 2), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Apply dilation to make text more prominent
    dilated = cv2.dilate(opening, kernel, iterations=1)
    
    return dilated

def cluster_pixels(img_array, n_clusters=3):
    """
    Cluster pixels to separate text, background, and noise.
    Returns a simplified image with clustered pixel values.
    """
    # Reshape image for clustering
    h, w = img_array.shape[:2]
    reshaped = img_array.reshape(-1, 3) if len(img_array.shape) == 3 else img_array.reshape(-1, 1)
    
    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(reshaped)
    
    # Create new image with cluster centers
    clustered_img = np.zeros_like(reshaped)
    for i in range(n_clusters):
        clustered_img[labels == i] = kmeans.cluster_centers_[i]
    
    # Reshape back to original dimensions
    clustered_img = clustered_img.reshape(img_array.shape)
    
    return clustered_img.astype(np.uint8)

def denoise_permuted_image(img_array):
    """
    Apply techniques to denoise the permuted image and make patterns more visible.
    """
    # Apply median blur to reduce salt-and-pepper noise
    denoised = cv2.medianBlur(img_array, 3)
    
    # Apply bilateral filter to preserve edges while smoothing
    if len(img_array.shape) == 3:
        denoised = cv2.bilateralFilter(denoised, 9, 75, 75)
    
    return denoised

def detect_character_blobs(img_array):
    """
    Detect character-like blobs in the image.
    Returns binary image with potential character regions.
    """
    # Convert to grayscale if needed
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array.copy()
    
    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    # Apply morphological operations to connect components
    kernel = np.ones((3, 3), np.uint8)
    closing = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    # Find contours
    contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by size
    min_area = 100
    max_area = 5000
    character_mask = np.zeros_like(gray)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_area < area < max_area:
            cv2.drawContours(character_mask, [contour], -1, 255, -1)
    
    return character_mask

def extract_character_from_image(img_array):
    """
    Extract the character from the image using various techniques.
    Returns the most likely character.
    """
    # Try multiple preprocessing approaches
    results = []
    
    # Approach 1: Basic OCR
    try:
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array.copy()
        
        # Apply preprocessing
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Run OCR
        text = pytesseract.image_to_string(binary, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        
        # Clean result
        text = text.strip()
        if text and len(text) >= 1:
            results.append(text[0])
    except Exception as e:
        print(f"OCR error: {e}")
    
    # Approach 2: Clustered image OCR
    try:
        clustered = cluster_pixels(img_array)
        text = pytesseract.image_to_string(clustered, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        text = text.strip()
        if text and len(text) >= 1:
            results.append(text[0])
    except Exception as e:
        print(f"Clustered OCR error: {e}")
    
    # Approach 3: Character blob detection
    try:
        blobs = detect_character_blobs(img_array)
        text = pytesseract.image_to_string(blobs, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        text = text.strip()
        if text and len(text) >= 1:
            results.append(text[0])
    except Exception as e:
        print(f"Blob OCR error: {e}")
    
    # Get most common result or fallback
    if results:
        counter = Counter(results)
        most_common = counter.most_common(1)[0][0]
        return most_common
    else:
        # Fallback: return a placeholder for manual inspection
        return '?'

def process_encrypted_image(filepath):
    """
    Process an encrypted image to extract the character.
    Returns the extracted character and path to processed image.
    """
    print(f"Processing {filepath}...")
    
    # Load image
    img_array, size = load_image(filepath)
    
    # Create visualization folder
    os.makedirs("processed_images", exist_ok=True)
    base_name = os.path.basename(filepath).split('.')[0]
    
    # Apply various processing techniques
    # 1. Denoise the permuted image
    denoised = denoise_permuted_image(img_array)
    Image.fromarray(denoised).save(f"processed_images/{base_name}_denoised.png")
    
    # 2. Cluster pixels
    clustered = cluster_pixels(img_array)
    Image.fromarray(clustered).save(f"processed_images/{base_name}_clustered.png")
    
    # 3. Character blob detection
    blobs = detect_character_blobs(img_array if len(img_array.shape) < 3 else cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY))
    Image.fromarray(blobs).save(f"processed_images/{base_name}_blobs.png")
    
    # 4. OCR preprocessing
    preprocessed = preprocess_for_ocr(img_array)
    Image.fromarray(preprocessed).save(f"processed_images/{base_name}_preprocessed.png")
    
    # Extract character
    character = extract_character_from_image(img_array)
    
    return character, f"processed_images/{base_name}_preprocessed.png"

def create_visualizations(image_paths, results):
    """Create visualizations of the processing results."""
    plt.figure(figsize=(15, 10))
    
    for i, (img_path, result) in enumerate(zip(image_paths, results)):
        if i >= 10:  # Limit to 10 examples for visualization
            break
        
        # Original image
        img = Image.open(img_path)
        img_array = np.array(img)
        
        # Create subplot
        plt.subplot(5, 4, i*2 + 1)
        plt.imshow(img_array)
        plt.title(f"Original {os.path.basename(img_path)}")
        plt.axis('off')
        
        # Processed image
        processed_path = f"processed_images/{os.path.basename(img_path).split('.')[0]}_preprocessed.png"
        if os.path.exists(processed_path):
            processed = Image.open(processed_path)
            plt.subplot(5, 4, i*2 + 2)
            plt.imshow(np.array(processed), cmap='gray')
            plt.title(f"Extracted: {result}")
            plt.axis('off')
    
    plt.tight_layout()
    plt.savefig("processing_results.png")
    plt.close()

def process_all_images():
    """
    Process all randomstring*.png images and extract the hidden string.
    Returns the extracted string.
    """
    # Find all encrypted images in the encrypted directory
    image_files = sorted([os.path.join(ENCRYPTED_DIR, f) for f in os.listdir(ENCRYPTED_DIR) 
                         if f.startswith('randomstring') and f.endswith('.png')])
    
    if not image_files:
        print(f"No matching encrypted images found in the '{ENCRYPTED_DIR}' directory.")
        return ""
    
    print(f"Found {len(image_files)} encrypted images.")
    
    # Process each image
    extracted_chars = []
    processed_paths = []
    
    for img_file in image_files:
        character, processed_path = process_encrypted_image(img_file)
        extracted_chars.append(character)
        processed_paths.append(processed_path)
        print(f"Image {os.path.basename(img_file)}: Extracted character '{character}'")
    
    # Create result string
    result_string = ''.join(extracted_chars)
    
    # Save result to output file
    with open("72_randomstring2.txt", "w") as f:
        f.write(result_string)
    
    print(f"Extracted string: {result_string}")
    print(f"Saved to 72_randomstring2.txt")
    
    # Create visualizations
    create_visualizations(image_files, extracted_chars)
    
    return result_string

if __name__ == "__main__":
    # Check if encrypted directory exists
    if not os.path.exists(ENCRYPTED_DIR):
        print(f"Error: Directory '{ENCRYPTED_DIR}' not found. Please create this directory and place encrypted images inside.")
    else:
        # Test with single image
        test_files = [f for f in os.listdir(ENCRYPTED_DIR) if f.startswith('randomstring') and f.endswith('.png')]
        if test_files:
            test_file = os.path.join(ENCRYPTED_DIR, test_files[0])
            print(f"Testing with {test_file}...")
            character, processed_path = process_encrypted_image(test_file)
            print(f"Test result: Character '{character}' extracted from {test_file}")
            
            # Process all images
            print("\nProcessing all images...")
            process_all_images()
        else:
            print(f"No matching images found in '{ENCRYPTED_DIR}' directory.")