from PIL import Image, ImageDraw, ImageFont
import math
import random


# ============================================================
# SHRISHA — TINY NEON PINK PARTICLE HEART
#
# HEARTBEAT
#     ↓
# HEART BURSTS
#     ↓
# PARTICLES FORM "SHRISHA"
#     ↓
# SHRISHA BURSTS
#     ↓
# PARTICLES REFORM HEART
#     ↓
# REPEAT
#
# Transparent background
# Pink particles ONLY
# ============================================================


# ============================================================
# SETTINGS
# ============================================================

W = 900
H = 260

FPS = 15
DURATION = 6.0
FRAMES = int(FPS * DURATION)

# More particles = denser / finer effect
N_PARTICLES = 950

TEXT = "SHRISHA"

FONT_SIZE = 105

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]


# ============================================================
# NEON PINK PALETTE
#
# Same pink hue throughout.
# Only brightness changes.
# ============================================================

PINK_DARK = (180, 5, 95)

PINK = (255, 15, 145)

PINK_HOT = (255, 35, 165)

PINK_BRIGHT = (255, 80, 195)

PINK_CORE = (255, 150, 220)


# ============================================================
# TRANSPARENCY KEY
# ============================================================

TRANSPARENT = (0, 255, 0)


# ============================================================
# FONT
# ============================================================

font = None

for path in FONT_PATHS:

    try:

        font = ImageFont.truetype(
            path,
            FONT_SIZE
        )

        print("Using font:", path)

        break

    except:

        pass


if font is None:

    raise RuntimeError(
        "Could not find a suitable font."
    )


# ============================================================
# RANDOM SEED
# ============================================================

random.seed(12345)


# ============================================================
# MATH HELPERS
# ============================================================

def lerp(a, b, t):

    return a + (b - a) * t


def smoothstep(t):

    t = max(
        0.0,
        min(1.0, t)
    )

    return t * t * (3.0 - 2.0 * t)


def ease_out(t):

    t = max(
        0.0,
        min(1.0, t)
    )

    return 1.0 - (1.0 - t) ** 3


def ease_in_out(t):

    return smoothstep(t)


# ============================================================
# CREATE HEART PARTICLES
# ============================================================

def create_heart_points(n):

    points = []

    while len(points) < n:

        t = random.uniform(
            0,
            2 * math.pi
        )

        # Random density inside the heart
        scale = random.uniform(
            0.35,
            1.0
        )

        # Mathematical heart
        x = (
            16
            * math.sin(t) ** 3
        )

        y = (
            13 * math.cos(t)
            - 5 * math.cos(2 * t)
            - 2 * math.cos(3 * t)
            - math.cos(4 * t)
        )

        x *= scale
        y *= scale

        px = (
            W / 2
            + x * 8.0
        )

        py = (
            H / 2
            - y * 7.0
        )

        points.append(
            (px, py)
        )

    return points


# ============================================================
# CREATE TEXT PARTICLES
# ============================================================

def create_text_points(
    text,
    n
):

    mask = Image.new(
        "L",
        (W, H),
        0
    )

    draw = ImageDraw.Draw(mask)

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    x = (
        W - text_width
    ) / 2

    y = (
        H - text_height
    ) / 2 - 10

    draw.text(
        (x, y),
        text,
        font=font,
        fill=255
    )

    pixels = []

    # Fine sampling gives the letters
    # a dense particle structure.
    for yy in range(
        0,
        H,
        2
    ):

        for xx in range(
            0,
            W,
            2
        ):

            if mask.getpixel(
                (xx, yy)
            ) > 180:

                pixels.append(
                    (xx, yy)
                )

    if not pixels:

        raise RuntimeError(
            "Could not create text mask."
        )

    return [
        random.choice(pixels)
        for _ in range(n)
    ]


# ============================================================
# TARGET POSITIONS
# ============================================================

heart_points = create_heart_points(
    N_PARTICLES
)

text_points = create_text_points(
    TEXT,
    N_PARTICLES
)


# ============================================================
# PARTICLE PERSONALITY
# ============================================================

particles = []

for i in range(
    N_PARTICLES
):

    particles.append({

        # MOST PARTICLES ARE TINY
        "size": random.choices(
            [1, 2, 3],
            weights=[
                82,
                16,
                2
            ],
            k=1
        )[0],

        # Individual sparkle brightness
        "brightness": random.uniform(
            0.75,
            1.0
        ),

        # Burst distance
        "burst": random.uniform(
            0.75,
            1.35
        ),

        # Random burst direction
        "angle": random.uniform(
            0,
            2 * math.pi
        ),

        # Individual sparkle timing
        "phase": random.uniform(
            0,
            2 * math.pi
        ),

        # Sparkle speed
        "sparkle_speed": random.uniform(
            9,
            16
        )
    })


# ============================================================
# HEARTBEAT
# ============================================================

def heartbeat(t):

    # First strong beat
    beat1 = math.exp(
        -(
            (t - 0.28)
            / 0.07
        ) ** 2
    )

    # Second smaller beat
    beat2 = math.exp(
        -(
            (t - 0.45)
            / 0.055
        ) ** 2
    )

    return (
        1.0
        + 0.12 * beat1
        + 0.07 * beat2
    )


# ============================================================
# PARTICLE POSITION
# ============================================================

def particle_position(
    i,
    time
):

    heart_x, heart_y = (
        heart_points[i]
    )

    text_x, text_y = (
        text_points[i]
    )

    p = particles[i]

    cx = W / 2
    cy = H / 2


    # ========================================================
    # 0.00 → 1.00
    # HEARTBEAT
    # ========================================================

    if time < 1.0:

        scale = heartbeat(
            time
        )

        x = (
            cx
            + (heart_x - cx)
            * scale
        )

        y = (
            cy
            + (heart_y - cy)
            * scale
        )

        return x, y


    # ========================================================
    # 1.00 → 1.45
    # HEART EXPLOSION
    # ========================================================

    if time < 1.45:

        t = (
            time - 1.0
        ) / 0.45

        t = ease_out(t)

        dx = heart_x - cx
        dy = heart_y - cy

        distance = math.sqrt(
            dx * dx
            + dy * dy
        ) + 0.001

        dx /= distance
        dy /= distance

        explosion = (
            25
            + 150
            * t
            * p["burst"]
        )

        x = (
            heart_x
            + dx * explosion
        )

        y = (
            heart_y
            + dy * explosion
        )

        # Organic sideways movement
        x += (
            math.cos(p["angle"])
            * 25
            * t
        )

        y += (
            math.sin(p["angle"])
            * 25
            * t
        )

        return x, y


    # ========================================================
    # 1.45 → 2.65
    # PARTICLES → SHRISHA
    # ========================================================

    if time < 2.65:

        t = (
            time - 1.45
        ) / 1.20

        t = ease_in_out(t)

        dx = heart_x - cx
        dy = heart_y - cy

        distance = math.sqrt(
            dx * dx
            + dy * dy
        ) + 0.001

        dx /= distance
        dy /= distance

        explosion = (
            100
            * p["burst"]
        )

        start_x = (
            heart_x
            + dx * explosion
        )

        start_y = (
            heart_y
            + dy * explosion
        )

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


    # ========================================================
    # 2.65 → 3.45
    # SHRISHA
    # ========================================================

    if time < 3.45:

        # Very subtle particle breathing
        movement = (
            math.sin(
                time * 8
                + p["phase"]
            )
            * 0.5
        )

        return (
            text_x + movement,
            text_y + movement
        )


    # ========================================================
    # 3.45 → 4.15
    # SHRISHA EXPLOSION
    # ========================================================

    if time < 4.15:

        t = (
            time - 3.45
        ) / 0.70

        t = ease_out(t)

        dx = text_x - cx
        dy = text_y - cy

        distance = math.sqrt(
            dx * dx
            + dy * dy
        ) + 0.001

        dx /= distance
        dy /= distance

        explosion = (
            20
            + 155
            * t
            * p["burst"]
        )

        x = (
            text_x
            + dx * explosion
        )

        y = (
            text_y
            + dy * explosion
        )

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


    # ========================================================
    # 4.15 → 5.15
    # PARTICLES → HEART
    # ========================================================

    if time < 5.15:

        t = (
            time - 4.15
        ) / 1.0

        t = ease_in_out(t)

        dx = text_x - cx
        dy = text_y - cy

        distance = math.sqrt(
            dx * dx
            + dy * dy
        ) + 0.001

        dx /= distance
        dy /= distance

        explosion = (
            110
            * p["burst"]
        )

        start_x = (
            text_x
            + dx * explosion
        )

        start_y = (
            text_y
            + dy * explosion
        )

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


    # ========================================================
    # 5.15 → 6.00
    # HEARTBEAT
    # ========================================================

    t = (
        time - 5.15
    ) / 0.85

    scale = heartbeat(t)

    x = (
        cx
        + (heart_x - cx)
        * scale
    )

    y = (
        cy
        + (heart_y - cy)
        * scale
    )

    return x, y


# ============================================================
# DRAW TINY NEON PINK PARTICLE
# ============================================================

def draw_particle_neon(
    draw,
    x,
    y,
    size,
    sparkle
):

    # ========================================================
    # VERY SMALL OUTER GLOW
    # ========================================================

    if size == 1:

        r1 = 2.5

    elif size == 2:

        r1 = 4

    else:

        r1 = 5


    draw.ellipse(
        (
            x - r1,
            y - r1,
            x + r1,
            y + r1
        ),
        fill=PINK_DARK
    )


    # ========================================================
    # NEON PINK MIDDLE
    # ========================================================

    if size == 1:

        r2 = 1.6

    elif size == 2:

        r2 = 2.3

    else:

        r2 = 3


    draw.ellipse(
        (
            x - r2,
            y - r2,
            x + r2,
            y + r2
        ),
        fill=PINK
    )


    # ========================================================
    # HOT PINK CORE
    # ========================================================

    r3 = max(
        1,
        size
    )

    draw.ellipse(
        (
            x - r3,
            y - r3,
            x + r3,
            y + r3
        ),
        fill=PINK_HOT
    )


    # ========================================================
    # RANDOM-LOOKING BUT DETERMINISTIC SPARKLE
    # ========================================================

    if sparkle > 0.92:

        r4 = 1

        draw.ellipse(
            (
                x - r4,
                y - r4,
                x + r4,
                y + r4
            ),
            fill=PINK_CORE
        )


# ============================================================
# DRAW FRAME
# ============================================================

def draw_frame(time):

    # Completely transparent canvas
    image = Image.new(
        "RGBA",
        (W, H),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(
        image
    )


    # ========================================================
    # PARTICLES
    # ========================================================

    for i in range(
        N_PARTICLES
    ):

        x, y = particle_position(
            i,
            time
        )

        p = particles[i]

        # Smooth individual sparkle
        sparkle = (
            0.5
            + 0.5
            * math.sin(
                time
                * p["sparkle_speed"]
                + p["phase"]
            )
        )

        draw_particle_neon(
            draw,
            x,
            y,
            p["size"],
            sparkle
        )


    return image


# ============================================================
# CONVERT RGBA → TRANSPARENT GIF FRAME
# ============================================================

def rgba_to_gif_frame(
    image
):

    # RGB canvas with transparency key
    rgb = Image.new(
        "RGB",
        (W, H),
        TRANSPARENT
    )

    # Paste visible pixels
    rgb.paste(
        image,
        mask=image.getchannel(
            "A"
        )
    )


    # ========================================================
    # QUANTIZE
    # ========================================================

    palette = rgb.quantize(
        colors=255,
        method=Image.Quantize.MEDIANCUT
    )


    # ========================================================
    # RESERVE PALETTE INDEX 0
    # FOR TRANSPARENCY
    # ========================================================

    old_palette = (
        palette.getpalette()
    )

    new_palette = [
        0,
        255,
        0
    ]

    new_palette.extend(
        old_palette[
            :3 * 255
        ]
    )

    new_palette += [
        0
    ] * (
        768
        - len(new_palette)
    )

    palette.putpalette(
        new_palette[:768]
    )


    # ========================================================
    # MARK TRANSPARENT PIXELS
    # ========================================================

    palette_pixels = (
        palette.load()
    )

    rgb_pixels = rgb.load()


    for yy in range(H):

        for xx in range(W):

            if (
                rgb_pixels[
                    xx,
                    yy
                ]
                == TRANSPARENT
            ):

                palette_pixels[
                    xx,
                    yy
                ] = 0

            else:

                palette_pixels[
                    xx,
                    yy
                ] = min(
                    255,
                    palette_pixels[
                        xx,
                        yy
                    ] + 1
                )


    return palette


# ============================================================
# GENERATE
# ============================================================

print()
print(
    "=========================================="
)

print(
    "   SHRISHA — TINY PINK NEON PARTICLES"
)

print(
    "=========================================="
)

print()

frames = []


for frame_number in range(
    FRAMES
):

    time = (
        frame_number
        / FPS
    )

    print(
        f"Generating frame "
        f"{frame_number + 1}"
        f"/{FRAMES}",
        end="\r"
    )

    rgba = draw_frame(
        time
    )

    gif_frame = (
        rgba_to_gif_frame(
            rgba
        )
    )

    frames.append(
        gif_frame
    )


# ============================================================
# SAVE
# ============================================================

# SAME FILE NAME AS BEFORE
output = "shrisha-neon.gif"


frames[0].save(
    output,
    save_all=True,
    append_images=frames[1:],
    duration=int(
        1000 / FPS
    ),
    loop=0,
    transparency=0,
    disposal=2,
    optimize=False
)


print()
print()

print(
    "=========================================="
)

print(
    "DONE ✨"
)

print(
    f"Created: {output}"
)

print(
    "Background: TRANSPARENT"
)

print(
    "Particles: TINY + NEON PINK"
)

print(
    "=========================================="
)