import os
import random
from PIL import Image

def find_largest_power_of_2_square(image):
    size = min(image.size)
    power_of_2 = 1
    while power_of_2 * 2 <= size:
        power_of_2 *= 2
    return power_of_2

def tile_image_regular(image, tile_size):
    new_size = 4096
    new_image = Image.new('RGB', (new_size, new_size))
    for x in range(0, new_size, tile_size):
        for y in range(0, new_size, tile_size):
            new_image.paste(image.crop((0, 0, tile_size, tile_size)), (x, y))
    return new_image

def tile_image_complex(image, tile_size):
    new_size = 4096
    new_image = Image.new('RGB', (new_size, new_size))

    # Randomly tile the entire 4K texture
    for x in range(0, new_size, tile_size):
        for y in range(0, new_size, tile_size):
            rand_x = random.randint(0, image.width - tile_size)
            rand_y = random.randint(0, image.height - tile_size)
            tile = image.crop((rand_x, rand_y, rand_x + tile_size, rand_y + tile_size))
            new_image.paste(tile, (x, y))

    return new_image

def main():
    print("Choose tiling method:")
    print("1. Regular Tiling")
    print("2. Complex Tiling")
    tiling_method = input("Enter 1 or 2: ")

    files = [f for f in os.listdir('.') if f.endswith('.png')]
    if not files:
        print("No PNG files found in the current directory.")
        return

    for i, file in enumerate(files):
        print(f"{i+1}. {file}")

    selected_file = None
    while selected_file is None:
        try:
            choice = int(input("Select a PNG file by number: ")) - 1
            if 0 <= choice < len(files):
                selected_file = files[choice]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    with Image.open(selected_file) as img:
        tile_size = find_largest_power_of_2_square(img)
        if tile_size == 4096:
            new_image = img
        else:
            if tiling_method == '1':
                new_image = tile_image_regular(img, tile_size)
            elif tiling_method == '2':
                new_image = tile_image_complex(img, tile_size)
            else:
                print("Invalid tiling method selected. Exiting.")
                return
        
        new_filename = f"{os.path.splitext(selected_file)[0]}_4k.png"
        new_image.save(new_filename)
        print(f"Image saved as {new_filename}")

if __name__ == "__main__":
    main()
