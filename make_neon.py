from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import random

# ============================================================
# SHRisha NEON PARTICLE HEART
#
# Animation:
#   HEART → heartbeat → burst → SHRISHA → dissolve → HEART
#
# Output:
#   shrisha-neon.gif
# ============================================================

# -----------------------------
# SETTINGS
# -----------------------------

W = 900
H = 260

FPS = 15

# One complete animation cycle
DURATION = 6.0
FRAMES = int(DURATION * FPS)

# Number of glowing particles
N_PARTICLES = 700

# Neon colours
PINK = (255, 35, 170)
HOT_PINK = (255, 80, 210)
PURPLE = (185, 60, 255)
WHITE_PINK = (255, 210, 245)

# Background
# BACKGROUND = (4, 4, 10) # pure black
BACKGROUND = (13, 17, 23) # github dark mode
# Text
TEXT = "SHRISHA"

# Font paths that work on GitHub Actions / Linux
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]

FONT_SIZE = 105


# ============================================================
# FIND FONT
# ============================================================

font = None

for path in FONT_PATHS:
    try:
        font = ImageFont.truetype(path, FONT_SIZE)
        print("Using font:", path)
        break
    except:
        pass

if font is None:
    raise RuntimeError("Could not find a suitable font.")


# ============================================================
# RANDOM SEED
# ============================================================

random.seed(42)


# ============================================================
# BASIC MATH
# ============================================================

def lerp(a, b, t):
    return a + (b - a) * t


def ease_in_out(t):
    """
    Smooth movement.
    """
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ease_out(t):
    """
    Fast beginning, slow ending.
    """
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = max(0.0, min(1.0, t))
    return t ** 3


# ============================================================
# HEART PARTICLE POSITIONS
# ============================================================

def create_heart_points(n):
    """
    Creates particles along a mathematical heart shape.

    Parametric heart:
        x = 16 sin^3(t)
        y = 13 cos(t)
           - 5 cos(2t)
           - 2 cos(3t)
           - cos(4t)
    """

    points = []

    # Fill the heart rather than only drawing the outline.
    # We generate many random points and keep those inside
    # the approximate heart boundary.
    attempts = 0

    while len(points) < n and attempts < n * 30:

        attempts += 1

        t = random.uniform(0, 2 * math.pi)

        scale = random.uniform(0.45, 1.0)

        x = 16 * math.sin(t) ** 3
        y = (
            13 * math.cos(t)
            - 5 * math.cos(2 * t)
            - 2 * math.cos(3 * t)
            - math.cos(4 * t)
        )

        x *= scale
        y *= scale

        # Heart size
        px = W / 2 + x * 8.2
        py = H / 2 - y * 7.0

        points.append((px, py))

    return points


# ============================================================
# TEXT PARTICLE POSITIONS
# ============================================================

def create_text_points(text, n):
    """
    Renders SHRISHA to a temporary mask and samples
    particles from the letters.
    """

    mask = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(mask)

    bbox = draw.textbbox((0, 0), text, font=font)

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (W - text_width) / 2
    y = (H - text_height) / 2 - 10

    draw.text(
        (x, y),
        text,
        font=font,
        fill=255,
    )

    # Find all pixels belonging to the letters
    pixels = []

    for yy in range(H):
        for xx in range(W):
            if mask.getpixel((xx, yy)) > 180:
                pixels.append((xx, yy))

    if not pixels:
        raise RuntimeError("Could not create text mask.")

    # Sample points
    points = []

    for _ in range(n):
        points.append(random.choice(pixels))

    return points


# ============================================================
# CREATE TARGETS
# ============================================================

heart_points = create_heart_points(N_PARTICLES)
text_points = create_text_points(TEXT, N_PARTICLES)

# Make sure both arrays have identical length
assert len(heart_points) == len(text_points)


# ============================================================
# PARTICLE PERSONALITY
# ============================================================

particles = []

for i in range(N_PARTICLES):

    # Slight random variation
    size = random.choice([1, 1, 1, 2, 2, 3])

    brightness = random.uniform(0.65, 1.0)

    # Different particles have slightly different burst distances
    burst_strength = random.uniform(0.7, 1.4)

    angle = random.uniform(0, math.pi * 2)

    particles.append({
        "size": size,
        "brightness": brightness,
        "burst_strength": burst_strength,
        "angle": angle,
    })


# ============================================================
# HEARTBEAT SCALE
# ============================================================

def heartbeat(t):
    """
    Gives the heart a subtle double-beat.

    This happens during the beginning/end of the animation.
    """

    # Two little pulses
    beat1 = math.exp(-((t - 0.35) / 0.08) ** 2)
    beat2 = math.exp(-((t - 0.52) / 0.06) ** 2)

    return 1.0 + 0.10 * beat1 + 0.06 * beat2


# ============================================================
# PARTICLE POSITION CALCULATION
# ============================================================

def particle_position(i, phase):

    heart_x, heart_y = heart_points[i]
    text_x, text_y = text_points[i]

    p = particles[i]

    # --------------------------------------------------------
    # PHASE 1
    # HEARTBEAT
    # 0.0 - 1.0 sec
    # --------------------------------------------------------

    if phase < 1.0:

        scale = heartbeat(phase)

        cx = W / 2
        cy = H / 2

        x = cx + (heart_x - cx) * scale
        y = cy + (heart_y - cy) * scale

        return x, y


    # --------------------------------------------------------
    # PHASE 2
    # HEART BURSTS
    # 1.0 - 1.45 sec
    # --------------------------------------------------------

    elif phase < 1.45:

        t = (phase - 1.0) / 0.45
        t = ease_out(t)

        cx = W / 2
        cy = H / 2

        # Direction from center
        dx = heart_x - cx
        dy = heart_y - cy

        length = math.sqrt(dx * dx + dy * dy) + 0.001

        dx /= length
        dy /= length

        # Particles explode outward
        distance = 25 + 130 * t * p["burst_strength"]

        x = heart_x + dx * distance
        y = heart_y + dy * distance

        # Additional random movement
        x += math.cos(p["angle"]) * 20 * t
        y += math.sin(p["angle"]) * 20 * t

        return x, y


    # --------------------------------------------------------
    # PHASE 3
    # PARTICLES FORM SHRISHA
    # 1.45 - 2.65 sec
    # --------------------------------------------------------

    elif phase < 2.65:

        t = (phase - 1.45) / 1.20
        t = ease_in_out(t)

        cx = W / 2
        cy = H / 2

        # Start from a burst cloud
        dx = heart_x - cx
        dy = heart_y - cy

        length = math.sqrt(dx * dx + dy * dy) + 0.001

        dx /= length
        dy /= length

        burst_distance = 100 * p["burst_strength"]

        start_x = heart_x + dx * burst_distance
        start_y = heart_y + dy * burst_distance

        # Move toward letters
        x = lerp(start_x, text_x, t)
        y = lerp(start_y, text_y, t)

        return x, y


    # --------------------------------------------------------
    # PHASE 4
    # SHRISHA HOLDS
    # 2.65 - 3.45 sec
    # --------------------------------------------------------

    elif phase < 3.45:

        # Tiny floating movement
        wiggle = math.sin(phase * 8 + i) * 0.8

        return text_x + wiggle, text_y


    # --------------------------------------------------------
    # PHASE 5
    # TEXT EXPLODES
    # 3.45 - 4.15 sec
    # --------------------------------------------------------

    elif phase < 4.15:

        t = (phase - 3.45) / 0.70
        t = ease_out(t)

        cx = W / 2
        cy = H / 2

        dx = text_x - cx
        dy = text_y - cy

        length = math.sqrt(dx * dx + dy * dy) + 0.001

        dx /= length
        dy /= length

        distance = 20 + 150 * t * p["burst_strength"]

        x = text_x + dx * distance
        y = text_y + dy * distance

        x += math.cos(p["angle"]) * 15 * t
        y += math.sin(p["angle"]) * 15 * t

        return x, y


    # --------------------------------------------------------
    # PHASE 6
    # PARTICLES RETURN TO HEART
    # 4.15 - 5.15 sec
    # --------------------------------------------------------

    elif phase < 5.15:

        t = (phase - 4.15) / 1.0
        t = ease_in_out(t)

        cx = W / 2
        cy = H / 2

        dx = text_x - cx
        dy = text_y - cy

        length = math.sqrt(dx * dx + dy * dy) + 0.001

        dx /= length
        dy /= length

        burst_distance = 110 * p["burst_strength"]

        start_x = text_x + dx * burst_distance
        start_y = text_y + dy * burst_distance

        x = lerp(start_x, heart_x, t)
        y = lerp(start_y, heart_y, t)

        return x, y


    # --------------------------------------------------------
    # PHASE 7
    # HEARTBEAT AGAIN
    # 5.15 - 6.0 sec
    # --------------------------------------------------------

    else:

        t = (phase - 5.15) / 0.85

        scale = heartbeat(t)

        cx = W / 2
        cy = H / 2

        x = cx + (heart_x - cx) * scale
        y = cy + (heart_y - cy) * scale

        return x, y


# ============================================================
# DRAW ONE FRAME
# ============================================================

def draw_frame(phase):

    base = Image.new(
        "RGBA",
        (W, H),
        (*BACKGROUND, 255)
    )

    # --------------------------------------------------------
    # GLOW LAYER
    # --------------------------------------------------------

    glow = Image.new(
        "RGBA",
        (W, H),
        (0, 0, 0, 0)
    )

    gd = ImageDraw.Draw(glow)

    for i in range(N_PARTICLES):

        x, y = particle_position(i, phase)

        p = particles[i]

        r = p["size"] * 2.5

        # Alternate pink/purple particles
        if i % 7 == 0:
            colour = PURPLE
        else:
            colour = PINK

        alpha = int(90 * p["brightness"])

        gd.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r
            ),
            fill=(
                colour[0],
                colour[1],
                colour[2],
                alpha
            )
        )

    # Blur the glow
    glow = glow.filter(
        ImageFilter.GaussianBlur(7)
    )

    base = Image.alpha_composite(
        base,
        glow
    )

    # --------------------------------------------------------
    # SHARP PARTICLES
    # --------------------------------------------------------

    particles_layer = Image.new(
        "RGBA",
        (W, H),
        (0, 0, 0, 0)
    )

    pd = ImageDraw.Draw(particles_layer)

    for i in range(N_PARTICLES):

        x, y = particle_position(i, phase)

        p = particles[i]

        size = p["size"]

        if i % 11 == 0:
            colour = WHITE_PINK
        elif i % 7 == 0:
            colour = PURPLE
        else:
            colour = HOT_PINK

        alpha = int(
            180 + 75 * p["brightness"]
        )

        pd.ellipse(
            (
                x - size,
                y - size,
                x + size,
                y + size
            ),
            fill=(
                colour[0],
                colour[1],
                colour[2],
                min(255, alpha)
            )
        )

    base = Image.alpha_composite(
        base,
        particles_layer
    )

    # --------------------------------------------------------
    # SUBTLE CENTRAL GLOW
    # --------------------------------------------------------

    center_glow = Image.new(
        "RGBA",
        (W, H),
        (0, 0, 0, 0)
    )

    cd = ImageDraw.Draw(center_glow)

    radius = 90

    cd.ellipse(
        (
            W / 2 - radius,
            H / 2 - radius,
            W / 2 + radius,
            H / 2 + radius
        ),
        fill=(255, 20, 170, 15)
    )

    center_glow = center_glow.filter(
        ImageFilter.GaussianBlur(40)
    )

    base = Image.alpha_composite(
        base,
        center_glow
    )

    return base


# ============================================================
# GENERATE GIF
# ============================================================

print("Generating neon particle animation...")

frames = []

for frame_number in range(FRAMES):

    phase = frame_number / FPS

    print(
        f"Frame {frame_number + 1}/{FRAMES}",
        end="\r"
    )

    frame = draw_frame(phase)

    # Convert to palette mode for GIF
    frames.append(
        frame.convert("P", palette=Image.Palette.ADAPTIVE)
    )


# ============================================================
# SAVE
# ============================================================

output = "shrisha-neon.gif"

frames[0].save(
    output,
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)

print()
print()
print("======================================")
print("Created:", output)
print("======================================")