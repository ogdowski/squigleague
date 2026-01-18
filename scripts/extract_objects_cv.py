"""Extract battlefield objects from battle plan images using computer vision"""
import cv2
import numpy as np
from pathlib import Path
import json

def analyze_passing_seasons():
    """Analyze Passing Seasons battle plan to extract object positions"""
    
    # Load the AOI image (most accurate source)
    img_path = Path("assets/battle-plans-ageofindex/aos-passing-seasons.png")
    img = cv2.imread(str(img_path))
    
    if img is None:
        print(f"ERROR: Could not load {img_path}")
        return None
    
    height, width = img.shape[:2]
    print(f"Image size: {width}x{height}")
    
    # Convert to HSV for color detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Detect circles (objectives are usually circular markers)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=30,
        param1=50,
        param2=30,
        minRadius=5,
        maxRadius=30
    )
    
    objects = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        print(f"\nFound {len(circles[0])} circular objects:")
        
        for i, (x, y, r) in enumerate(circles[0]):
            # Sample color at circle center
            color_sample = hsv[y, x]
            h, s, v = color_sample
            
            # Determine color based on HSV
            if s < 50:
                color = "white/gray"
            elif 20 < h < 40:
                color = "yellow/gold"
            elif 40 < h < 80:
                color = "green"
            elif 0 < h < 20 or h > 160:
                color = "red/brown"
            elif 80 < h < 140:
                color = "blue"
            else:
                color = "unknown"
            
            # Convert pixel coordinates to battlefield coordinates
            # Assume battlefield is 60"x44" and centered in image
            # This needs calibration based on actual image layout
            battlefield_x = (x / width) * 60
            battlefield_y = (y / height) * 44
            
            obj = {
                "type": "objective",
                "x": round(battlefield_x, 1),
                "y": round(battlefield_y, 1),
                "color": color,
                "pixel_pos": [int(x), int(y)],
                "radius": int(r)
            }
            objects.append(obj)
            print(f"  {i+1}. Position ({obj['x']}\", {obj['y']}\") - {color} - radius {r}px at ({x}, {y})")
    
    # Save annotated image for verification
    if circles is not None:
        img_annotated = img.copy()
        for x, y, r in circles[0]:
            cv2.circle(img_annotated, (x, y), r, (0, 255, 0), 2)
            cv2.circle(img_annotated, (x, y), 2, (0, 0, 255), 3)
        
        output_path = Path("temp_passing_seasons_analyzed.png")
        cv2.imwrite(str(output_path), img_annotated)
        print(f"\nSaved annotated image to {output_path}")
    
    return objects

if __name__ == "__main__":
    print("Analyzing Passing Seasons battle plan...")
    objects = analyze_passing_seasons()
    
    if objects:
        print(f"\nExtracted {len(objects)} objects:")
        print(json.dumps(objects, indent=2))
