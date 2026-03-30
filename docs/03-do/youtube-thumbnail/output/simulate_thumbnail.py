from PIL import Image, ImageDraw, ImageFont
import os

img_path = r"C:\Users\user\.gemini\antigravity\brain\10354156-1c3b-4173-aa38-0a7e1b600f7e\screen_glow_bg_1774551349766.png"
output_path = r"C:\Users\user\.gemini\antigravity\brain\10354156-1c3b-4173-aa38-0a7e1b600f7e\final_thumbnail.png"

try:
    img = Image.open(img_path).convert("RGBA")
except Exception as e:
    print(f"Image load error: {e}")
    exit(1)

draw = ImageDraw.Draw(img)

# Try loading malgun.ttf (Malgun Gothic)
try:
    font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 90)
    font_sub = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 100)
except:
    font = ImageFont.load_default()
    font_sub = ImageFont.load_default()

text1 = "AI 활용"
text2 = "100% 마스터"

# text_area: { "x": 780, "y": 100, "w": 480, "h": 560 }
x = 750
y = 250

def draw_text_with_outline(draw, x, y, text, font, text_color, outline_color, outline_width=5):
    # Shadow
    draw.text((x + 5, y + 5), text, font=font, fill=(0, 0, 0, 128))
    # Outline
    for dx in range(-outline_width, outline_width+1):
        for dy in range(-outline_width, outline_width+1):
            if dx*dx + dy*dy <= outline_width*outline_width:
                draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
    # Inside
    draw.text((x, y), text, font=font, fill=text_color)

# Draw text 1 (Yellow)
draw_text_with_outline(draw, x, y, text1, font_sub, "#FFD600", "#0D1B2A")

# Draw text 2 (White)
draw_text_with_outline(draw, x, y + 120, text2, font, "#FFFFFF", "#0D1B2A")

img.save(output_path, "PNG")
print(f"Thumbnail saved to {output_path}")
