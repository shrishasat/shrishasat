from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

W, H = 1000, 260
FRAMES = 48

# Change this if you have a preferred font
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font = ImageFont.truetype(FONT, 105)

frames = []

for frame in range(FRAMES):

    # dark background
    base = Image.new("RGBA", (W, H), (5, 5, 12, 255))

    # --- neon glow ---
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)

    text = "🧠  SHRISHA"

    bbox = gd.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x = (W - tw) // 2
    y = (H - th) // 2 - 8

    # purple/blue/pink neon layers
    for blur, alpha in [(30, 70), (18, 100), (8, 160)]:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)

        ld.text(
            (x, y),
            text,
            font=font,
            fill=(150, 40, 255, alpha),
            stroke_width=3,
            stroke_fill=(255, 20, 180, alpha),
        )

        layer = layer.filter(ImageFilter.GaussianBlur(blur))
        glow = Image.alpha_composite(glow, layer)

    base = Image.alpha_composite(base, glow)

    # --- main text ---
    text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(text_layer)

    td.text(
        (x, y),
        text,
        font=font,
        fill=(245, 245, 255, 255),
        stroke_width=3,
        stroke_fill=(130, 60, 255, 255),
    )

    # --- moving shine ---
    shine_x = int(
        x - 150 + (tw + 300) * (frame / (FRAMES - 1))
    )

    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)

    md.rectangle(
        (shine_x - 45, 0, shine_x + 45, H),
        fill=255
    )

    # gradient-ish shine
    shine = Image.new("RGBA", (W, H), (255, 50, 220, 0))
    shine.putalpha(mask)

    # composite shine onto text
    text_layer = Image.alpha_composite(text_layer, shine)

    base = Image.alpha_composite(base, text_layer)

    frames.append(base.convert("P"))

frames[0].save(
    "shrisha-neon.gif",
    save_all=True,
    append_images=frames[1:],
    duration=55,
    loop=0,
    optimize=True,
)

print("Created shrisha-neon.gif")
