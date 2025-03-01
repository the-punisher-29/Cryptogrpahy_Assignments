import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import itertools

# Define Total Variation and Neighboring Pixel Correlation functions
def total_variation(image):
    """Calculate the total variation of an image."""
    tv = np.sum(np.abs(np.diff(image, axis=0))) + np.sum(np.abs(np.diff(image, axis=1)))
    return tv

def neighboring_pixel_correlation(image):
    """Calculate the average correlation between neighboring pixels."""
    horizontal_corr = np.corrcoef(image[:, :-1].flatten(), image[:, 1:].flatten())[0, 1]
    vertical_corr = np.corrcoef(image[:-1, :].flatten(), image[1:, :].flatten())[0, 1]
    return (horizontal_corr + vertical_corr) / 2

# Decrypt a single image by trying all possible permutations
def decrypt_image(img, perm_size):
    """Decrypt an image by testing permutations to minimize Total Variation."""
    gray_img = np.array(img.convert("L"))
    best_tv_score = float('inf')
    best_perm = None
    best_image = None

    # Generate all possible permutations (for simplicity, assume small perm_size)
    for perm in itertools.permutations(range(perm_size)):
        # Apply permutation to pixel values
        flat_pixels = gray_img.flatten()
        reordered_pixels = [flat_pixels[i] for i in perm]
        reshaped_img = np.array(reordered_pixels).reshape(gray_img.shape)

        # Calculate Total Variation score
        tv_score = total_variation(reshaped_img)
        if tv_score < best_tv_score:
            best_tv_score = tv_score
            best_perm = perm
            best_image = reshaped_img

    return best_image, best_perm

# Main function to process all images in a directory
def main():
    encrypted_dir = 'encrypted'
    output_dir = 'decrypted'
    
    if not os.path.exists(encrypted_dir):
        print("Encrypted directory not found!")
        return
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # List all encrypted images
    encrypted_images = [f for f in os.listdir(encrypted_dir) if f.endswith('.png')]
    encrypted_images.sort()  # Ensure consistent order
    
    recovered_string = ""
    
    for idx, fname in enumerate(encrypted_images):
        img_path = os.path.join(encrypted_dir, fname)
        img = Image.open(img_path)

        # Decrypt the image by minimizing randomness (e.g., TV score)
        decrypted_img, _ = decrypt_image(img, perm_size=img.size[0] * img.size[1])

        # Save the decrypted image with a new name
        out_name = f"randomstring{idx:02d}.png"
        Image.fromarray(decrypted_img).save(os.path.join(output_dir, out_name))
        
        # Optionally extract text from the decrypted image using OCR (if pytesseract is installed)
        try:
            import pytesseract
            text = pytesseract.image_to_string(Image.fromarray(decrypted_img), config='--psm 7').strip()
            recovered_string += text
        except ImportError:
            print("pytesseract not installed. Skipping OCR.")
    
    # Save the recovered random string to a file
    output_file = "yourserialno_randomstring2.txt"
    with open(output_file, "w") as f:
        f.write(recovered_string)
    
    print("Recovered random string:", recovered_string)
    print("Decrypted images have been saved in the '{}' directory.".format(output_dir))
    print("Random string written to file:", output_file)

if __name__ == '__main__':
    main()
