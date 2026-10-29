"""
Mock data and synthetic construction asset generator.
Creates sample construction site frames, architectural blueprints, concrete crack textures,
and historical safety/progress datasets so the platform works out-of-the-box.
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def generate_sample_safety_frame(filepath: Path = None) -> Image.Image:
    """
    Generate a synthetic construction site CCTV camera frame showing workers
    and hazard zones for safety compliance testing.
    """
    w, h = 960, 540
    img = Image.new("RGB", (w, h), color=(140, 150, 160)) # Concrete / gravel tone
    draw = ImageDraw.Draw(img, "RGBA")

    # Horizon and sky/steel framing
    draw.rectangle([0, 0, w, 220], fill=(185, 205, 225))
    
    # Tower Crane structure in background
    crane_x = 520
    draw.rectangle([crane_x, 30, crane_x + 24, 340], fill=(234, 88, 12)) # Crane mast
    draw.line([crane_x - 180, 50, crane_x + 360, 50], fill=(234, 88, 12), width=6) # Jib
    draw.line([crane_x + 220, 50, crane_x + 220, 240], fill=(50, 50, 50), width=2) # Hoist line
    draw.rectangle([crane_x + 205, 240, crane_x + 235, 275], fill=(70, 70, 70)) # Suspended cargo crate

    # Structural Steel Grid (I-Beams)
    for bx in range(80, w, 220):
        draw.rectangle([bx, 100, bx + 16, 420], fill=(75, 85, 99))
    draw.rectangle([50, 220, w - 50, 235], fill=(55, 65, 81)) # Horizontal girder

    # Zone A (Crane Swing / Suspended Load Drop Zone) Marker - dashed yellow/black border
    zone_x1, zone_y1, zone_x2, zone_y2 = 420, 240, 760, 510
    draw.rectangle([zone_x1, zone_y1, zone_x2, zone_y2], fill=(239, 68, 68, 40), outline=(239, 68, 68, 200), width=2)
    draw.text((zone_x1 + 10, zone_y1 + 10), "ZONE A: CRANE RADIUS (NO ENTRY UNDER LOAD)", fill=(239, 68, 68, 255))

    # Worker 1 (Left - Fully Compliant with Yellow Hardhat + Hi-Vis Green Vest)
    w1_x, w1_y = 220, 240
    # Head & Yellow Hardhat
    draw.ellipse([w1_x + 16, w1_y - 28, w1_x + 48, w1_y + 4], fill=(250, 204, 21)) # Yellow Helmet
    draw.ellipse([w1_x + 22, w1_y - 6, w1_x + 42, w1_y + 14], fill=(225, 175, 140)) # Face
    # Torso & Hi-Vis Vest
    draw.rectangle([w1_x + 10, w1_y + 14, w1_x + 54, w1_y + 80], fill=(74, 222, 128)) # Hi-vis green
    draw.rectangle([w1_x + 20, w1_y + 14, w1_x + 26, w1_y + 80], fill=(230, 230, 230)) # Reflective tape
    draw.rectangle([w1_x + 38, w1_y + 14, w1_x + 44, w1_y + 80], fill=(230, 230, 230))
    # Legs / Boots
    draw.rectangle([w1_x + 14, w1_y + 80, w1_x + 28, w1_y + 145], fill=(30, 41, 59))
    draw.rectangle([w1_x + 36, w1_y + 80, w1_x + 50, w1_y + 145], fill=(30, 41, 59))
    draw.rectangle([w1_x + 10, w1_y + 145, w1_x + 30, w1_y + 160], fill=(120, 53, 15)) # Steel boot
    draw.rectangle([w1_x + 34, w1_y + 145, w1_x + 54, w1_y + 160], fill=(120, 53, 15))

    # Worker 2 (Center inside Crane Zone - VIOLATION: NO HARDHAT + INSIDE EXCLUSION ZONE)
    w2_x, w2_y = 540, 270
    # Head (NO HARDHAT, dark hair)
    draw.ellipse([w2_x + 20, w2_y - 18, w2_x + 44, w2_y + 8], fill=(30, 20, 15)) # Hair
    draw.ellipse([w2_x + 22, w2_y - 4, w2_x + 42, w2_y + 16], fill=(215, 160, 130)) # Face
    # Torso (Orange vest)
    draw.rectangle([w2_x + 12, w2_y + 16, w2_x + 52, w2_y + 82], fill=(249, 115, 22))
    # Legs / Boots
    draw.rectangle([w2_x + 16, w2_y + 82, w2_x + 28, w2_y + 145], fill=(51, 65, 85))
    draw.rectangle([w2_x + 36, w2_y + 82, w2_x + 48, w2_y + 145], fill=(51, 65, 85))
    draw.rectangle([w2_x + 14, w2_y + 145, w2_x + 30, w2_y + 158], fill=(20, 20, 20))
    draw.rectangle([w2_x + 34, w2_y + 145, w2_x + 50, w2_y + 158], fill=(20, 20, 20))

    # Worker 3 (Right - Fully Compliant with White Hardhat + Hi-Vis Orange Vest)
    w3_x, w3_y = 780, 230
    draw.ellipse([w3_x + 16, w3_y - 28, w3_x + 48, w3_y + 4], fill=(248, 250, 252)) # White Helmet
    draw.ellipse([w3_x + 22, w3_y - 6, w3_x + 42, w3_y + 14], fill=(230, 180, 145))
    draw.rectangle([w3_x + 10, w3_y + 14, w3_x + 54, w3_y + 80], fill=(249, 115, 22)) # Orange vest
    draw.rectangle([w3_x + 14, w3_y + 80, w3_x + 28, w3_y + 145], fill=(30, 41, 59))
    draw.rectangle([w3_x + 36, w3_y + 80, w3_x + 50, w3_y + 145], fill=(30, 41, 59))
    draw.rectangle([w3_x + 10, w3_y + 145, w3_x + 30, w3_y + 160], fill=(120, 53, 15))
    draw.rectangle([w3_x + 34, w3_y + 145, w3_x + 54, w3_y + 160], fill=(120, 53, 15))

    # Onscreen CCTV HUD overlay
    draw.rectangle([10, 10, 310, 48], fill=(15, 23, 42, 200))
    draw.text((18, 14), "CAM-04 [EAST TOWER HOIST & BAY 2]", fill=(248, 250, 252, 255))
    draw.text((18, 30), "LIVE FEED | 1080p 30fps | AI ACTIVE", fill=(52, 211, 153, 255))

    if filepath:
        img.save(filepath, quality=95)
    return img

def generate_sample_blueprint(filepath: Path = None) -> Image.Image:
    """
    Generate an architectural CAD blueprint diagram with grid lines, rooms,
    fire exits, structural columns, and dimension annotations.
    """
    w, h = 900, 600
    img = Image.new("RGB", (w, h), color=(15, 30, 60)) # Classic blueprint cyan-navy
    draw = ImageDraw.Draw(img)

    # Grid background lines
    for x in range(0, w, 30):
        draw.line([x, 0, x, h], fill=(25, 45, 85), width=1)
    for y in range(0, h, 30):
        draw.line([0, y, w, y], fill=(25, 45, 85), width=1)

    # Architectural Exterior Perimeter Walls
    draw.rectangle([100, 80, 800, 520], outline=(255, 255, 255), width=4)

    # Interior Partitions
    # Central corridor
    draw.line([100, 280, 800, 280], fill=(255, 255, 255), width=3)
    draw.line([100, 340, 800, 340], fill=(255, 255, 255), width=3)

    # Room divider walls
    draw.line([320, 80, 320, 280], fill=(255, 255, 255), width=2)
    draw.line([560, 80, 560, 280], fill=(255, 255, 255), width=2)
    draw.line([400, 340, 400, 520], fill=(255, 255, 255), width=2)
    draw.line([640, 340, 640, 520], fill=(255, 255, 255), width=2)

    # Structural Columns (Solid white squares with cross)
    columns = [
        (100, 80), (320, 80), (560, 80), (800, 80),
        (100, 280), (320, 280), (560, 280), (800, 280),
        (100, 340), (320, 340), (560, 340), (800, 340),
        (100, 520), (320, 520), (560, 520), (800, 520),
    ]
    for cx, cy in columns:
        draw.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 255, 255))
        draw.line([cx - 8, cy - 8, cx + 8, cy + 8], fill=(15, 30, 60), width=1)
        draw.line([cx - 8, cy + 8, cx + 8, cy - 8], fill=(15, 30, 60), width=1)

    # Room labels and dimensions
    draw.text((150, 160), "ELECTRICAL ROOM #101\n18' - 6\" x 24' - 0\"", fill=(180, 220, 255))
    draw.text((380, 160), "HVAC MECHANICAL SHAFT\n14' - 0\" x 24' - 0\"", fill=(180, 220, 255))
    draw.text((620, 160), "TELECOM / SERVER CLOSET\n16' - 4\" x 24' - 0\"", fill=(180, 220, 255))
    draw.text((360, 302), "MAIN CENTRAL CIRCULATION CORRIDOR (WIDTH: 8'-0\")", fill=(255, 230, 120))
    draw.text((180, 410), "EMERGENCY STAIR 1 (2-HR FIRE ENCLOSURE)", fill=(255, 160, 160))
    draw.text((470, 410), "COMMERCIAL LEASABLE BAY A", fill=(180, 220, 255))
    draw.text((690, 410), "RESTROOM SUITE", fill=(180, 220, 255))

    # Door swing arcs
    draw.arc([305, 260, 345, 300], 180, 270, fill=(255, 255, 255), width=1)
    draw.arc([545, 260, 585, 300], 180, 270, fill=(255, 255, 255), width=1)

    # Title Block
    draw.rectangle([580, 460, 790, 510], fill=(20, 40, 80), outline=(255, 255, 255), width=1)
    draw.text((590, 465), "APEX TOWER - LEVEL 2 PLAN", fill=(255, 255, 255))
    draw.text((590, 480), "DWG NO: A-102 | REV 4 | SCALE: 1/4\" = 1'-0\"", fill=(180, 220, 255))
    draw.text((590, 495), "ARCHITECT: KPF PARTNERS | PE STAMP VALID", fill=(120, 240, 180))

    if filepath:
        img.save(filepath, quality=95)
    return img

def generate_sample_drone_progress(filepath_planned: Path = None, filepath_actual: Path = None):
    """
    Generate a pair of drone/site images:
    1. Planned baseline CAD/BIM model
    2. Actual drone capture showing current progress & completed framing
    """
    w, h = 800, 500
    
    # Baseline (Scheduled Model: Completed framing + partial cladding)
    img_plan = Image.new("RGB", (w, h), color=(220, 228, 235))
    dp = ImageDraw.Draw(img_plan)
    # Sky / Ground
    dp.rectangle([0, 0, w, 150], fill=(190, 215, 240))
    dp.rectangle([0, 380, w, h], fill=(130, 140, 150))
    # Completed Building Silhouette
    dp.rectangle([150, 120, 650, 380], fill=(240, 245, 250), outline=(70, 80, 95), width=3)
    # Windows grid
    for floor_y in range(150, 360, 50):
        for col_x in range(180, 620, 60):
            dp.rectangle([col_x, floor_y, col_x + 40, floor_y + 35], fill=(140, 180, 215), outline=(90, 110, 130))
    dp.text((20, 20), "BASELINE BIM SCHEDULE (WEEK 18 TARGET - 75% PLANNED)", fill=(20, 40, 70))

    # Actual Drone Capture (Current reality: steel erected, lower floors framed, upper open)
    img_act = Image.new("RGB", (w, h), color=(200, 210, 220))
    da = ImageDraw.Draw(img_act)
    da.rectangle([0, 0, w, 150], fill=(175, 200, 230))
    da.rectangle([0, 380, w, h], fill=(140, 135, 125)) # Muddy site terrain
    
    # Structural concrete lower core
    da.rectangle([150, 240, 650, 380], fill=(180, 185, 190), outline=(80, 85, 90), width=2)
    # Windows installed only on ground & 1st level
    for col_x in range(180, 620, 60):
        da.rectangle([col_x, 300, col_x + 40, 335], fill=(130, 170, 205), outline=(70, 90, 110))
    
    # Upper steel skeleton only (in progress, not yet enclosed)
    for bx in range(180, 630, 60):
        da.rectangle([bx, 130, bx + 10, 240], fill=(180, 83, 9)) # Red-lead primer steel
    for fy in range(160, 250, 40):
        da.line([150, fy, 650, fy], fill=(180, 83, 9), width=4)
        
    da.text((20, 20), "ACTUAL DRONE CAPTURE (WEEK 18 FLIGHT - 68% EARNED VALUE)", fill=(30, 50, 80))
    da.text((20, 40), "VARIANCE: -7% (Glazing delivery delay on Level 2-3)", fill=(220, 38, 38))

    if filepath_planned:
        img_plan.save(filepath_planned, quality=95)
    if filepath_actual:
        img_act.save(filepath_actual, quality=95)

    return img_plan, img_act

def generate_sample_concrete_crack(filepath: Path = None) -> Image.Image:
    """
    Generate a high-resolution concrete surface texture with realistic shear crack fissure
    for automated defect and structural crack inspection testing.
    """
    w, h = 800, 550
    # Concrete base texture with Perlin-like noise
    base = np.random.normal(160, 18, (h, w)).clip(80, 220).astype(np.uint8)
    img = Image.fromarray(base).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Draw meandering crack path
    points = []
    x = 180
    y = 60
    points.append((x, y))
    
    rng = np.random.RandomState(42)
    while y < 480 and x < 720:
        x += int(rng.normal(6, 10))
        y += int(rng.uniform(12, 28))
        points.append((x, y))

    # Main crack fissure (dark with jagged branch fissures)
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=(30, 30, 30), width=3)
        # Random micro-fissure branch
        if i % 3 == 0:
            bx = points[i][0] + int(rng.uniform(-30, 35))
            by = points[i][1] + int(rng.uniform(-10, 25))
            draw.line([points[i], (bx, by)], fill=(45, 45, 45), width=1)

    # Add measurement metric scale bar in bottom left
    draw.rectangle([40, 480, 240, 515], fill=(255, 255, 255), outline=(0, 0, 0), width=1)
    draw.line([60, 498, 220, 498], fill=(0, 0, 0), width=2)
    draw.line([60, 490, 60, 506], fill=(0, 0, 0), width=2)
    draw.line([220, 490, 220, 506], fill=(0, 0, 0), width=2)
    draw.text((90, 484), "SCALE: 40 mm", fill=(0, 0, 0))

    if filepath:
        img.save(filepath, quality=95)
    return img

def ensure_sample_assets(target_dir: Path):
    """Ensure all sample images exist in target directory."""
    target_dir.mkdir(parents=True, exist_ok=True)
    f1 = target_dir / "sample_site_safety.jpg"
    f2 = target_dir / "sample_blueprint.png"
    f3 = target_dir / "sample_drone_planned.jpg"
    f4 = target_dir / "sample_drone_actual.jpg"
    f5 = target_dir / "sample_concrete_crack.jpg"

    if not f1.exists():
        generate_sample_safety_frame(f1)
    if not f2.exists():
        generate_sample_blueprint(f2)
    if not f3.exists() or not f4.exists():
        generate_sample_drone_progress(f3, f4)
    if not f5.exists():
        generate_sample_concrete_crack(f5)
