import os
from PIL import Image

# Folder containing your PNG files
folder = "rename_i"  # change to your folder path
output_log = "dimensions_mm.txt"

DPI = 300
INCH_TO_MM = 25.4

def px_to_mm(px):
    return (px / DPI) * INCH_TO_MM

results = []

for filename in os.listdir(folder):
    if filename.lower().endswith(".png"):
        filepath = os.path.join(folder, filename)

        with Image.open(filepath) as img:
            width_px, height_px = img.size

        width_mm = px_to_mm(width_px)
        height_mm = px_to_mm(height_px)

        # Format to 3 decimal places
        width_mm_str = f"{width_mm:.3f}"
        height_mm_str = f"{height_mm:.3f}"

        name, ext = os.path.splitext(filename)
        new_name = f"{name}_{width_mm_str}x{height_mm_str}mm{ext}"
        new_path = os.path.join(folder, new_name)

        os.rename(filepath, new_path)

        results.append(f"{new_name}: {width_mm_str} mm x {height_mm_str} mm")

# Write results to file
with open(output_log, "w") as f:
    for line in results:
        f.write(line + "\n")

print("Done! Files renamed and dimensions saved.")