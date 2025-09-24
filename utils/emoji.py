from PIL import Image, ImageDraw, ImageFont
import os
import string

import discord as disc
from dotenv import load_dotenv

# Read in token from env
load_dotenv()
token = os.getenv("TOKEN")
client = disc.Client(application_id=945734352157933569, intents=disc.Intents.all())

colors = {
    "green": "#6aaa64",
    "yellow": "#c9b458",
    "black": "#3a3a3c",
    "gray": "#787c7e"
}

modes = {
    "gray": "#d3d6da",
    "black": "#3a3a3c",
}

# Settings
canvas_size = (128, 128)
transparent = (0, 0, 0, 0)
text_color = (255, 255, 255)  # Green (RGB for #4CAF50)
corner_radius = 10
border = 10
font_size = 90
output_folder = "emojis"

# Load font (you can change this to any .ttf file you have)
font = ImageFont.truetype("emojis/FranklinDemi.ttf", font_size)

# Generate images for A-Z
for color, background_color in colors.items():
    for letter in string.ascii_uppercase:
        img = Image.new("RGBA", canvas_size, transparent)
        draw = ImageDraw.Draw(img)

        # Rounded corners
        draw.rounded_rectangle(
            [(border, border), (canvas_size[0] - border, canvas_size[1] - border)],
            radius=corner_radius,
            fill=background_color
        )

        # Get text size and position
        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center the text
        x = (canvas_size[0] - text_width) / 2 - bbox[0]
        y = (canvas_size[1] - text_height) / 2 - bbox[1]

        # Draw the letter
        draw.text((x, y), letter, font=font, fill=text_color)

        # Save the image
        img.save(os.path.join(output_folder, color, f"{letter}_{color}.png"))

for color, background_color in modes.items():
    img = Image.new("RGBA", canvas_size, transparent)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [(border, border), (canvas_size[0] - border, canvas_size[1] - border)],
        radius=corner_radius,
        fill=background_color
    )

    # Carve out inner rectangle (make center transparent)
    inner_border = border * 1.7
    draw.rounded_rectangle(
        [(inner_border, inner_border), 
         (canvas_size[0] - inner_border, canvas_size[1] - inner_border)],
        radius=corner_radius - border,
        fill=transparent
    )

    # Save the image
    img.save(os.path.join(output_folder, "blank", f"BLANK_{color}.png"))

@client.event
async def on_ready():
    for color, background_color in colors.items():
        for letter in string.ascii_uppercase:
            with open(os.path.join(output_folder, color, f"{letter}_{color}.png"), "rb") as img_file:
                img_bytes = img_file.read()
                await client.create_application_emoji(name=f"{letter}_{color}", image=img_bytes)

    for color, background_color in modes.items():
        with open(os.path.join(output_folder, "blank", f"BLANK_{color}.png"), "rb") as img_file:
            img_bytes = img_file.read()
            await client.create_application_emoji(name=f"BLANK_{color}", image=img_bytes)
    await client.close()

client.run(token)
print("✅ Emoji letter set created!")