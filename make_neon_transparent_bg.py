from PIL import Image, ImageDraw, ImageFont
import math
import random


# ============================================================
# SHRISHA — PINK NEON PARTICLE HEART
#
# HEART → HEARTBEAT → BURST → SHRISHA
#       → BURST → HEART → repeat
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

N_PARTICLES = 650

TEXT = "SHRISHA"

FONT_SIZE = 105

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]


# ============================================================
# PINK PALETTE
#
# SAME PINK HUE
# Different brightness only
# ============================================================

PINK_DARK = (180, 5, 95)

PINK = (255, 20, 150)

PINK_HOT = (255, 45, 175)

PINK_BRIGHT = (255, 100, 200)

PINK_CORE = (255, 180, 225)


# ============================================================
# GIF TRANSPARENCY KEY
#
# This colour is never drawn.
# It is reserved for transparent pixels.
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

    return (
        t * t * (3.0 - 2.0 * t)
    )


def ease_out(t):

    t = max(
        0.0,
        min(1.0, t)
    )

    return 1.0 - (
        1.0 - t
    ) ** 3


def ease_in_out(t):

    return smoothstep(t)


# ============================================================
# HEART PARTICLES
# ============================================================

def create_heart_points(n):

    points = []

    while len(points) < n:

        t = random.uniform(
            0,
            2 * math.pi
        )

        # Controls how full the heart is
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

        # Position on canvas
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
# TEXT PARTICLES
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

    # Sample the letters
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
# CREATE HEART + TEXT TARGETS
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

        # Particle size
        "size": random.choice([
            1,
            1,
            1,
            2,
            2,
            3
        ]),

        # Brightness
        "brightness": random.uniform(
            0.70,
            1.0
        ),

        # How far it flies during burst
        "burst": random.uniform(
            0.75,
            1.35
        ),

        # Random explosion direction
        "angle": random.uniform(
            0,
            2 * math.pi
        ),

        # Tiny individual timing variation
        "phase": random.uniform(
            0,
            2 * math.pi
        )
    })


# ============================================================
# HEARTBEAT
# ============================================================

def heartbeat(t):

    # Strong first beat
    beat1 = math.exp(
        -(
            (t - 0.28)
            / 0.07
        ) ** 2
    )

    # Smaller second beat
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
    # PHASE 1
    #
    # 0.00 → 1.00
    #
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
    # PHASE 2
    #
    # 1.00 → 1.45
    #
    # HEART BURSTS
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

        # Slight sideways randomness
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
    # PHASE 3
    #
    # 1.45 → 2.65
    #
    # PARTICLES FORM SHRISHA
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
    # PHASE 4
    #
    # 2.65 → 3.45
    #
    # SHRISHA HOLDS
    # ========================================================

    if time < 3.45:

        movement = (
            math.sin(
                time * 8
                + p["phase"]
            )
            * 0.7
        )

        return (
            text_x + movement,
            text_y + movement
        )


    # ========================================================
    # PHASE 5
    #
    # 3.45 → 4.15
    #
    # SHRISHA EXPLODES
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
    # PHASE 6
    #
    # 4.15 → 5.15
    #
    # PARTICLES RETURN TO HEART
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
    # PHASE 7
    #
    # 5.15 → 6.00
    #
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
# DRAW ONE PINK NEON PARTICLE
# ============================================================

def draw_particle_neon(
    draw,
    x,
    y,
    size
):

    # --------------------------------------------------------
    # OUTER PINK GLOW
    # --------------------------------------------------------

    r1 = size * 5

    draw.ellipse(
        (
            x - r1,
            y - r1,
            x + r1,
            y + r1
        ),
        fill=PINK_DARK
    )


    # --------------------------------------------------------
    # MEDIUM PINK GLOW
    # --------------------------------------------------------

    r2 = size * 3.2

    draw.ellipse(
        (
            x - r2,
            y - r2,
            x + r2,
            y + r2
        ),
        fill=PINK
    )


    # --------------------------------------------------------
    # HOT PINK
    # --------------------------------------------------------

    r3 = size * 2

    draw.ellipse(
        (
            x - r3,
            y - r3,
            x + r3,
            y + r3
        ),
        fill=PINK_HOT
    )


    # --------------------------------------------------------
    # BRIGHT PINK CORE
    # --------------------------------------------------------

    r4 = max(
        1,
        size
    )

    draw.ellipse(
        (
            x - r4,
            y - r4,
            x + r4,
            y + r4
        ),
        fill=PINK_BRIGHT
    )


    # --------------------------------------------------------
    # TINY LIGHT-PINK CORE
    # --------------------------------------------------------

    if size >= 2:

        r5 = max(
            1,
            size * 0.45
        )

        draw.ellipse(
            (
                x - r5,
                y - r5,
                x + r5,
                y + r5
            ),
            fill=PINK_CORE
        )


# ============================================================
# DRAW FRAME
# ============================================================

def draw_frame(time):

    # --------------------------------------------------------
    # COMPLETELY TRANSPARENT BACKGROUND
    # --------------------------------------------------------

    image = Image.new(
        "RGBA",
        (W, H),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(
        image
    )


    # --------------------------------------------------------
    # DRAW EVERY PARTICLE
    # --------------------------------------------------------

    for i in range(
        N_PARTICLES
    ):

        x, y = particle_position(
            i,
            time
        )

        size = particles[i]["size"]

        draw_particle_neon(
            draw,
            x,
            y,
            size
        )


    return image


# ============================================================
# CONVERT RGBA → TRANSPARENT GIF
# ============================================================

def rgba_to_gif_frame(
    image
):

    # Create RGB image using the reserved
    # transparency colour.
    rgb = Image.new(
        "RGB",
        (W, H),
        TRANSPARENT
    )

    # Paste the neon particles over it.
    rgb.paste(
        image,
        mask=image.getchannel(
            "A"
        )
    )


    # --------------------------------------------------------
    # Quantize to GIF
    # --------------------------------------------------------

    palette = rgb.quantize(
        colors=255,
        method=Image.Quantize.MEDIANCUT
    )


    # --------------------------------------------------------
    # Reserve palette index 0
    # for transparency.
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Replace transparency-key pixels
    # --------------------------------------------------------

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
# GENERATE ANIMATION
# ============================================================

print()
print(
    "=========================================="
)

print(
    "   SHRISHA PINK NEON PARTICLE HEART"
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
        f"Generating "
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
    "DONE!"
)

print(
    f"Created: {output}"
)

print(
    "Background: TRANSPARENT"
)

print(
    "Particles: PINK ONLY"
)

print(
    "=========================================="
)