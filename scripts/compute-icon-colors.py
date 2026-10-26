#!/usr/bin/env python3
"""
Compute dominant colors for app icons and update apps.js with dominantColor field.
Run from project root: python3 scripts/compute-icon-colors.py
"""
import json
import os
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

ICONS_DIR = Path("launcher/icons")
APPS_JS = Path("launcher/apps.js")

def compute_dominant_color(image_path, sample_size=12):
    """Compute dominant color from image using small sample (like original JS)."""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Resize to small size for sampling (matches original 12x12 canvas)
            img_small = img.resize((sample_size, sample_size), Image.Resampling.LANCZOS)
            pixels = list(img_small.getdata())
            
            # Filter out transparent/near-transparent pixels (alpha < 128)
            # Since we converted to RGB, we don't have alpha - but we can skip very dark/light
            # Original JS: skip pixels with alpha < 128, then find max saturation * value
            valid_pixels = [p for p in pixels if not (p[0] < 10 and p[1] < 10 and p[2] < 10)]
            
            if not valid_pixels:
                return None
            
            # Convert to HSV and find pixel with max saturation * value (like original)
            def rgb_to_hsv(r, g, b):
                r, g, b = r / 255.0, g / 255.0, b / 255.0
                mx = max(r, g, b)
                mn = min(r, g, b)
                df = mx - mn
                if mx == mn:
                    h = 0
                elif mx == r:
                    h = (60 * ((g - b) / df) + 360) % 360
                elif mx == g:
                    h = (60 * ((b - r) / df) + 120) % 360
                else:
                    h = (60 * ((r - g) / df) + 240) % 360
                s = 0 if mx == 0 else df / mx
                v = mx
                return h, s, v
            
            best_pixel = None
            best_score = -1
            sum_r = sum_g = sum_b = 0
            count = 0
            
            for r, g, b in valid_pixels:
                h, s, v = rgb_to_hsv(r, g, b)
                # Original: score = saturation * min(1, 1.4 * value)
                score = s * min(1.0, 1.4 * v)
                if score > best_score:
                    best_score = score
                    best_pixel = (r, g, b)
                sum_r += r
                sum_g += g
                sum_b += b
                count += 1
            
            if best_score < 0.25:
                # Low saturation - use average color with boosted saturation (like original)
                avg_r, avg_g, avg_b = sum_r // count, sum_g // count, sum_b // count
                h, s, v = rgb_to_hsv(avg_r, avg_g, avg_b)
                v = max(v, 0.55)
                s = max(s, 0.55)
                # Convert back to RGB
                c = v * s
                x = c * (1 - abs((h / 60) % 2 - 1))
                m = v - c
                if h < 60:
                    r, g, b = c, x, 0
                elif h < 120:
                    r, g, b = x, c, 0
                elif h < 180:
                    r, g, b = 0, c, x
                elif h < 240:
                    r, g, b = 0, x, c
                elif h < 300:
                    r, g, b = x, 0, c
                else:
                    r, g, b = c, 0, x
                return [int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)]
            
            # Boost saturation slightly like original
            h, s, v = rgb_to_hsv(*best_pixel)
            s = min(1.0, 1.1 * s)
            v = max(0.5, v)
            c = v * s
            x = c * (1 - abs((h / 60) % 2 - 1))
            m = v - c
            if h < 60:
                r, g, b = c, x, 0
            elif h < 120:
                r, g, b = x, c, 0
            elif h < 180:
                r, g, b = 0, c, x
            elif h < 240:
                r, g, b = 0, x, c
            elif h < 300:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x
            return [int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)]
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def parse_apps_js(content):
    """Extract TV_APPS object from apps.js"""
    # Find window.TV_APPS = { ... };
    match = re.search(r'window\.TV_APPS\s*=\s*(\{.*?\});', content, re.DOTALL)
    if not match:
        raise ValueError("Could not find TV_APPS in apps.js")
    return json.loads(match.group(1))

def update_apps_js(tv_apps):
    """Write updated apps.js with dominantColor fields"""
    # Read original to preserve formatting
    with open(APPS_JS, 'r') as f:
        content = f.read()
    
    # Update each app with dominantColor
    for app in tv_apps['apps']:
        icon_rel = app.get('icon', '')
        # Strip "icons/" prefix if present
        if icon_rel.startswith('icons/'):
            icon_rel = icon_rel[6:]
        icon_path = ICONS_DIR / icon_rel
        if icon_path.exists():
            color = compute_dominant_color(icon_path)
            if color:
                app['dominantColor'] = color
                print(f"  {app['id']}: dominantColor = {color}")
            else:
                print(f"  {app['id']}: failed to compute color")
        else:
            print(f"  {app['id']}: icon not found at {icon_path}")
    
    # Reconstruct the JS object
    js_content = "// Generated by sync-apps.py: the TV's apps and inputs.\nwindow.TV_APPS = "
    js_content += json.dumps(tv_apps, indent=2)
    js_content += ";\n"
    
    with open(APPS_JS, 'w') as f:
        f.write(js_content)
    
    print(f"\nUpdated {APPS_JS}")

def main():
    print("Reading apps.js...")
    with open(APPS_JS, 'r') as f:
        content = f.read()
    
    tv_apps = parse_apps_js(content)
    print(f"Found {len(tv_apps['apps'])} apps")
    
    print("\nComputing dominant colors...")
    update_apps_js(tv_apps)
    print("\nDone!")

if __name__ == '__main__':
    main()