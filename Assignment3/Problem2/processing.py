import os
import numpy as np
from PIL import Image

def print_pixel_values(image, image_name):
    """Prints the pixel values of the image."""
    pixels = np.array(image)
    print(f"\nPixel values of {image_name}:")
    print(pixels)

def total_variation(image):
    """Calculate the total variation of an image."""
    tv = np.sum(np.abs(np.diff(image, axis=0))) + np.sum(np.abs(np.diff(image, axis=1)))
    return tv

def neighboring_pixel_correlation(image):
    """Calculate the average correlation between neighboring pixels."""
    try:
        horizontal_corr = np.corrcoef(image[:, :-1].flatten(), image[:, 1:].flatten())[0, 1]
        vertical_corr = np.corrcoef(image[:-1, :].flatten(), image[1:, :].flatten())[0, 1]
        return (horizontal_corr + vertical_corr) / 2
    except Exception:
        return None  # Handle cases where correlation cannot be calculated

def histogram_statistics(image):
    """Calculate histogram statistics for an image."""
    hist, _ = np.histogram(image.flatten(), bins=256, range=(0, 255))
    mean_intensity = np.mean(image)
    std_intensity = np.std(image)
    return hist, mean_intensity, std_intensity

def analyze_images(directory):
    """Analyzes all images in a given directory."""
    images = [f for f in os.listdir(directory) if f.startswith('randomstring') and f.endswith('.png')]
    images.sort()  # Ensure consistent order
    
    for img_name in images:
        img_path = os.path.join(directory, img_name)
        img = Image.open(img_path).convert("L")  # Convert to grayscale
        img_array = np.array(img)
        
        print(f"\nAnalyzing {img_name}...")
        
        # Print Pixel Values
        print_pixel_values(img_array, img_name)
        
        # Calculate Total Variation
        tv = total_variation(img_array)
        print(f"Total Variation (TV): {tv}")
        
        # Calculate Neighboring Pixel Correlation
        corr = neighboring_pixel_correlation(img_array)
        if corr is not None:
            print(f"Neighboring Pixel Correlation: {corr}")
        else:
            print("Neighboring Pixel Correlation: Could not be calculated.")
        
        # Calculate Histogram Statistics
        hist, mean_intensity, std_intensity = histogram_statistics(img_array)
        print(f"Histogram Mean Intensity: {mean_intensity}")
        print(f"Histogram Standard Deviation: {std_intensity}")
        print(f"Histogram (first 10 bins): {hist[:10]}")

def main():
    encrypted_dir = "."  # Current directory containing randomstringXX.png files
    
    if not os.path.exists(encrypted_dir):
        print("Directory not found!")
        return
    
    analyze_images(encrypted_dir)

if __name__ == "__main__":
    main()
