from PIL import Image, ImageDraw, ImageFont
import math
import random

# ============================================================
# SHRISHA — TRANSPARENT NEON PARTICLE ANIMATION
#
# HEART → BURST → SHRISHA → BURST → HEART
#
# Transparent GIF suitable for GitHub README
# ============================================================

# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

W = 900
H = 260

FPS = 15
DURATION = 6.0
FRAMES = int(FPS * DURATION)

N_PARTICLES = 650

TEXT = "SHRISHA"

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]

FONT_SIZE = 105

# ------------------------------------------------------------
# NEON COLOURS
# ------------------------------------------------------------

PINK = (255, 35, 170)
HOT_PINK = (255, 70, 195)
LIGHT_PINK = (255, 150, 225)
PURPLE = (190, 60, 255)
WHITE_PINK = (255, 220, 248)

# Reserved colour for GIF transparency.
# Do NOT use this colour for particles.
TRANSPARENT = (0, 255, 0)


# ============================================================
# FONT
# ============================================================

font = None

for path in FONT_PATHS:
    try:
        font = ImageFont.truetype(path, FONT_SIZE)
        print("Using:", path)
        break
    except:
        pass

if font is None:
    raise RuntimeError("No suitable font found.")


# ============================================================
# RANDOMNESS
# ============================================================

random.seed(12345)


# ============================================================
# HELPERS
# ============================================================

def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return smoothstep(t)


# ============================================================
# HEART
# ============================================================

def create_heart_points(n):

    points = []

    while len(points) < n:

        t = random.uniform(0, 2 * math.pi)

        # Random radius makes the heart look particle-based
        scale = random.uniform(0.35, 1.0)

        x = 16 * math.sin(t) ** 3

        y = (
            13 * math.cos(t)
            - 5 * math.cos(2 * t)
            - 2 * math.cos(3 * t)
            - math.cos(4 * t)
        )

        x *= scale
        y *= scale

        px = W / 2 + x * 8.0
        py = H / 2 - y * 7.0

        points.append((px, py))

    return points


# ============================================================
# TEXT
# ============================================================

def create_text_points(text, n):

    mask = Image.new("L", (W, H), 0)

    draw = ImageDraw.Draw(mask)

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x = (W - tw) / 2
    y = (H - th) / 2 - 10

    draw.text(
        (x, y),
        text,
        font=font,
        fill=255
    )

    pixels = []

    # Sample every few pixels instead of checking everything
    for yy in range(0, H, 2):

        for xx in range(0, W, 2):

            if mask.getpixel((xx, yy)) > 180:
                pixels.append((xx, yy))

    if not pixels:
        raise RuntimeError("Could not create text mask.")

    return [
        random.choice(pixels)
        for _ in range(n)
    ]


# ============================================================
# TARGET POSITIONS
# ============================================================

heart_points = create_heart_points(N_PARTICLES)

text_points = create_text_points(
    TEXT,
    N_PARTICLES
)


# ============================================================
# PARTICLE PERSONALITIES
# ============================================================

particles = []

for i in range(N_PARTICLES):

    particles.append({

        "size": random.choice([
            1, 1, 1,
            2, 2,
            3
        ]),

        "brightness": random.uniform(
            0.65,
            1.0
        ),

        "burst": random.uniform(
            0.75,
            1.35
        ),

        "angle": random.uniform(
            0,
            2 * math.pi
        ),

        "speed": random.uniform(
            0.7,
            1.3
        ),

        "phase": random.uniform(
            0,
            2 * math.pi
        )
    })


# ============================================================
# HEARTBEAT
# ============================================================

def heartbeat(t):

    # First strong beat
    beat1 = math.exp(
        -((t - 0.28) / 0.07) ** 2
    )

    # Second smaller beat
    beat2 = math.exp(
        -((t - 0.45) / 0.055) ** 2
    )

    return (
        1.0
        + 0.12 * beat1
        + 0.07 * beat2
    )


# ============================================================
# PARTICLE POSITION
# ============================================================

def particle_position(i, time):

    heart_x, heart_y = heart_points[i]
    text_x, text_y = text_points[i]

    p = particles[i]

    cx = W / 2
    cy = H / 2

    # --------------------------------------------------------
    # 0.00 → 1.00
    # HEARTBEAT
    # --------------------------------------------------------

    if time < 1.0:

        scale = heartbeat(time)

        x = cx + (heart_x - cx) * scale
        y = cy + (heart_y - cy) * scale

        return x, y


    # --------------------------------------------------------
    # 1.00 → 1.45
    # HEART EXPLOSION
    # --------------------------------------------------------

    if time < 1.45:

        t = (time - 1.0) / 0.45
        t = ease_out(t)

        dx = heart_x - cx
        dy = heart_y - cy

        distance = math.sqrt(
            dx * dx + dy * dy
        ) + 0.001

        dx /= distance
        dy /= distance

        explosion = (
            25
            + 150 * t * p["burst"]
        )

        x = heart_x + dx * explosion
        y = heart_y + dy * explosion

        x += math.cos(p["angle"]) * 25 * t
        y += math.sin(p["angle"]) * 25 * t

        return x, y


    # --------------------------------------------------------
    # 1.45 → 2.65
    # PARTICLES → SHRISHA
    # --------------------------------------------------------

    if time < 2.65:

        t = (time - 1.45) / 1.20
        t = ease_in_out(t)

        dx = heart_x - cx
        dy = heart_y - cy

        distance = math.sqrt(
            dx * dx + dy * dy
        ) + 0.001

        dx /= distance
        dy /= distance

        explosion = (
            100 * p["burst"]
        )

        start_x = heart_x + dx * explosion
        start_y = heart_y + dy * explosion

        x = lerp(
            start_x,
            text_x,
            t
        )

        y = lerp(
            start_y,
            text_y,
            t
        )

        return x, y


    # --------------------------------------------------------
    # 2.65 → 3.45
    # SHRISHA
    # --------------------------------------------------------

    if time < 3.45:

        tiny_motion = (
            math.sin(
                time * 8
                + p["phase"]
            )
            * 0.7
        )

        return (
            text_x + tiny_motion,
            text_y + tiny_motion
        )


    # --------------------------------------------------------
    # 3.45 → 4.15
    # SHRISHA EXPLODES
    # --------------------------------------------------------

    if time < 4.15:

        t = (time - 3.45) / 0.70
        t = ease_out(t)

        dx = text_x - cx
        dy = text_y - cy

        distance = math.sqrt(
            dx * dx + dy * dy
        ) + 0.001

        dx /= distance
        dy /= distance

        explosion = (
            20
            + 155 * t * p["burst"]
        )

        x = text_x + dx * explosion
        y = text_y + dy * explosion

        x += (
            math.cos(p["angle"])
            * 20
            * t
        )

        y += (
            math.sin(p["angle"])
            * 20
            * t
        )

        return x, y


    # --------------------------------------------------------
    # 4.15 → 5.15
    # PARTICLES → HEART
    # --------------------------------------------------------

    if time < 5.15:

        t = (time - 4.15) / 1.0
        t = ease_in_out(t)

        dx = text_x - cx
        dy = text_y - cy

        distance = math.sqrt(
            dx * dx + dy * dy
        ) + 0.001

        dx /= distance
        dy /= distance

        explosion = (
            110 * p["burst"]
        )

        start_x = text_x + dx * explosion
        start_y = text_y + dy * explosion

        x = lerp(
            start_x,
            heart_x,
            t
        )

        y = lerp(
            start_y,
            heart_y,
            t
        )

        return x, y


    # --------------------------------------------------------
    # 5.15 → 6.00
    # HEARTBEAT
    # --------------------------------------------------------

    t = (time - 5.15) / 0.85

    scale = heartbeat(t)

    x = cx + (heart_x - cx) * scale
    y = cy + (heart_y - cy) * scale

    return x, y


# ============================================================
# DRAW PARTICLES
# ============================================================

def draw_particle_neon(
    draw,
    x,
    y,
    size,
    colour,
    brightness
):

    # --------------------------------------------------------
    # Outer "glow"
    #
    # GIF can't store smooth alpha, so we create the
    # neon appearance using several increasingly bright
    # concentric circles.
    # --------------------------------------------------------

    # Very faint outer particle
    r1 = size * 4

    draw.ellipse(
        (
            x - r1,
            y - r1,
            x + r1,
            y + r1
        ),
        fill=(
            int(colour[0] * 0.28),
            int(colour[1] * 0.28),
            int(colour[2] * 0.28)
        )
    )

    # Medium glow
    r2 = size * 2.5

    draw.ellipse(
        (
            x - r2,
            y - r2,
            x + r2,
            y + r2
        ),
        fill=(
            int(colour[0] * 0.50),
            int(colour[1] * 0.50),
            int(colour[2] * 0.50)
        )
    )

    # Bright core
    r3 = max(1, size)

    draw.ellipse(
        (
            x - r3,
            y - r3,
            x + r3,
            y + r3
        ),
        fill=colour
    )


# ============================================================
# DRAW FRAME
# ============================================================

def draw_frame(time):

    # TRUE TRANSPARENT CANVAS
    image = Image.new(
        "RGBA",
        (W, H),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(image)

    # --------------------------------------------------------
    # PARTICLES
    # --------------------------------------------------------

    for i in range(N_PARTICLES):

        x, y = particle_position(
            i,
            time
        )

        p = particles[i]

        brightness = p["brightness"]

        # Occasional purple particles
        if i % 13 == 0:

            colour = PURPLE

        elif i % 17 == 0:

            colour = LIGHT_PINK

        elif i % 23 == 0:

            colour = WHITE_PINK

        else:

            colour = PINK

        # Random brightness variation
        colour = tuple(
            min(
                255,
                int(c * brightness)
            )
            for c in colour
        )

        draw_particle_neon(
            draw,
            x,
            y,
            p["size"],
            colour,
            brightness
        )

    return image


# ============================================================
# GIF PALETTE WITH TRANSPARENCY
# ============================================================

def rgba_to_transparent_gif_frame(image):

    # Convert RGBA to RGB first.
    #
    # We use the reserved green colour for pixels that
    # should become transparent.
    rgb = Image.new(
        "RGB",
        (W, H),
        TRANSPARENT
    )

    rgb.paste(
        image,
        mask=image.getchannel("A")
    )

    # Quantize to GIF palette
    palette = rgb.quantize(
        colors=255,
        method=Image.Quantize.MEDIANCUT
    )

    # Reserve palette index 0 for transparency.
    #
    # Create a new palette whose first colour is the
    # transparent key.
    old_palette = palette.getpalette()

    new_palette = [0, 255, 0]

    # Copy remaining palette colours
    new_palette.extend(
        old_palette[:3 * 255]
    )

    # Ensure exactly 768 values
    new_palette = (
        new_palette
        + [0] * (768 - len(new_palette))
    )

    palette.putpalette(new_palette[:768])

    # Find pixels matching our reserved transparent colour
    pixels = palette.load()

    rgb_pixels = rgb.load()

    for yy in range(H):

        for xx in range(W):

            if rgb_pixels[xx, yy] == TRANSPARENT:

                pixels[xx, yy] = 0

            else:

                # Shift all normal colours by one
                # because palette index 0 is reserved.
                pixels[xx, yy] = min(
                    255,
                    pixels[xx, yy] + 1
                )

    return palette


# ============================================================
# GENERATE
# ============================================================

print()
print("==========================================")
print(" SHRISHA NEON PARTICLE HEART")
print("==========================================")
print()

frames = []

for frame_number in range(FRAMES):

    time = frame_number / FPS

    print(
        f"Generating frame "
        f"{frame_number + 1}/{FRAMES}",
        end="\r"
    )

    rgba = draw_frame(time)

    gif_frame = rgba_to_transparent_gif_frame(
        rgba
    )

    frames.append(gif_frame)


# ============================================================
# SAVE GIF
# ============================================================

output = "shrisha-neon.gif"

frames[0].save(
    output,
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,

    # Important for transparent animation
    transparency=0,
    disposal=2,

    optimize=False
)

print()
print()
print("==========================================")
print("DONE!")
print("Created:", output)
print("Transparent background: YES")
print("==========================================")
