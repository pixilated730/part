import cv2
import numpy as np
from PIL import Image
import stepic

def enhance_contrast(image):
    """Increase contrast and brightness."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced_l = clahe.apply(l)
    
    # Merge channels back
    enhanced_lab = cv2.merge([enhanced_l, a, b])
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    return enhanced

def detect_edges(image):
    """Apply multiple edge detection methods."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Canny edge detection
    canny = cv2.Canny(gray, 50, 150)
    
    # Sobel edge detection
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel = np.sqrt(sobel_x**2 + sobel_y**2)
    sobel = np.uint8(sobel * 255 / np.max(sobel))
    
    return canny, sobel

def analyze_channels(image):
    """Analyze individual color channels and create heat maps."""
    # Split into channels
    b, g, r = cv2.split(image)
    
    # Create heatmaps
    heatmap_b = cv2.applyColorMap(b, cv2.COLORMAP_JET)
    heatmap_g = cv2.applyColorMap(g, cv2.COLORMAP_JET)
    heatmap_r = cv2.applyColorMap(r, cv2.COLORMAP_JET)
    
    return heatmap_b, heatmap_g, heatmap_r

def extract_hidden_data(image_path):
    """Try to extract hidden data using stepic."""
    try:
        img = Image.open(image_path)
        hidden_data = stepic.decode(img)
        return hidden_data if hidden_data else "No hidden data found"
    except Exception as e:
        return f"Error extracting data: {str(e)}"

def process_image(image_path):
    """Process image with multiple techniques to reveal hidden content."""
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return

    # Create output directory
    import os
    output_dir = "analysis_output"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Enhanced contrast
    enhanced = enhance_contrast(image)
    cv2.imwrite(f"{output_dir}/enhanced.png", enhanced)

    # 2. Edge detection
    canny, sobel = detect_edges(image)
    cv2.imwrite(f"{output_dir}/edges_canny.png", canny)
    cv2.imwrite(f"{output_dir}/edges_sobel.png", sobel)

    # 3. Channel analysis
    heatmap_b, heatmap_g, heatmap_r = analyze_channels(image)
    cv2.imwrite(f"{output_dir}/heatmap_blue.png", heatmap_b)
    cv2.imwrite(f"{output_dir}/heatmap_green.png", heatmap_g)
    cv2.imwrite(f"{output_dir}/heatmap_red.png", heatmap_r)

    # 4. Try different threshold techniques
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    cv2.imwrite(f"{output_dir}/threshold_binary.png", binary)
    cv2.imwrite(f"{output_dir}/threshold_adaptive.png", adaptive)

    # 5. Extract hidden data
    hidden_data = extract_hidden_data(image_path)
    with open(f"{output_dir}/hidden_data.txt", 'w') as f:
        f.write(hidden_data)

    print(f"""
Image Analysis Complete!
Results saved in '{output_dir}' directory:
- enhanced.png: Contrast enhanced image
- edges_canny.png: Canny edge detection
- edges_sobel.png: Sobel edge detection
- heatmap_[color].png: Channel heatmaps
- threshold_binary.png: Binary threshold
- threshold_adaptive.png: Adaptive threshold
- hidden_data.txt: Extracted hidden data

Hidden data found: {hidden_data}
    """)

if __name__ == "__main__":
    # Install required packages if not already installed
    # pip install opencv-python pillow stepic numpy
    
    image_path = "2.webp"  # Change this to your image path
    process_image(image_path)