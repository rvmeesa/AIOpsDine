from PIL import Image

# Generate empty table (white)
Image.new("RGB", (200, 200), "white").save("data/sample_frames/empty_table.png")

# Generate occupied table (gray)
Image.new("RGB", (200, 200), "gray").save("data/sample_frames/occupied_table.png")