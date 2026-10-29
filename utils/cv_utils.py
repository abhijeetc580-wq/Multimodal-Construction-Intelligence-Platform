"""
Computer Vision utilities for bounding box annotations, image format conversions,
crack defect contour analysis, and visual difference overlays.
"""

import io
from typing import List, Dict, Any, Tuple
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    """Convert a PIL Image to OpenCV BGR numpy array."""
    rgb = np.array(pil_img.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

def cv2_to_pil(cv_img: np.ndarray) -> Image.Image:
    """Convert OpenCV BGR numpy array to PIL Image."""
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)

def image_to_bytes(img: Image.Image, format: str = "JPEG") -> bytes:
    """Convert PIL image to byte stream."""
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()

def draw_safety_annotations(
    image: Image.Image,
    detections: List[Dict[str, Any]],
    danger_zone: Dict[str, Any] = None
) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Draw bounding boxes, PPE badges, and danger zone boundaries on a site frame.
    Returns the annotated PIL Image and a summary dict of compliance statistics.
    """
    img_draw = image.copy()
    draw = ImageDraw.Draw(img_draw, "RGBA")
    w, h = img_draw.size

    # Draw Danger Zone if defined
    if danger_zone:
        box = danger_zone.get("box", [0.45, 0.45, 0.95, 0.95]) # [ymin, xmin, ymax, xmax] normalized
        ymin, xmin, ymax, xmax = [int(box[0]*h), int(box[1]*w), int(box[2]*h), int(box[3]*w)]
        zone_color = danger_zone.get("color", (239, 68, 68, 45)) # semi-transparent red
        draw.rectangle([xmin, ymin, xmax, ymax], fill=zone_color, outline=(239, 68, 68, 220), width=3)
        draw.text((xmin + 8, ymin + 8), f"DANGER ZONE: {danger_zone.get('name', 'Restricted')}", fill=(255, 255, 255, 255))

    total_workers = 0
    compliant_workers = 0
    violations = []

    for idx, det in enumerate(detections):
        det_type = det.get("type", "worker")
        box = det.get("box", [0, 0, 0, 0])
        ymin, xmin, ymax, xmax = [int(box[0]*h), int(box[1]*w), int(box[2]*h), int(box[3]*w)]
        
        if det_type == "worker":
            total_workers += 1
            has_hardhat = det.get("hardhat", False)
            has_vest = det.get("hi_vis_vest", False)
            has_boots = det.get("safety_boots", True)
            in_danger_zone = det.get("in_danger_zone", False)

            is_compliant = has_hardhat and has_vest and not in_danger_zone
            if is_compliant:
                compliant_workers += 1
                box_color = (16, 185, 129, 255) # Emerald Green
                status_label = f"Worker #{idx+1} [COMPLIANT]"
            else:
                box_color = (239, 68, 68, 255) # Crimson Red
                issues = []
                if not has_hardhat:
                    issues.append("No Hardhat (OSHA 1926.100)")
                if not has_vest:
                    issues.append("No Hi-Vis Vest (ANSI 107)")
                if in_danger_zone:
                    issues.append("Zone A Intrusion")
                status_label = f"Worker #{idx+1} [ALERT: {', '.join(issues)}]"
                violations.append({
                    "worker_id": f"Worker #{idx+1}",
                    "issues": issues,
                    "location": f"X: {xmin}-{xmax}, Y: {ymin}-{ymax}",
                    "severity": "CRITICAL" if in_danger_zone or (not has_hardhat and not has_vest) else "HIGH"
                })

            # Bounding box
            draw.rectangle([xmin, ymin, xmax, ymax], outline=box_color, width=3)
            
            # Badge header
            badge_h = 24
            draw.rectangle([xmin, max(0, ymin - badge_h), xmin + len(status_label)*8 + 12, ymin], fill=box_color)
            draw.text((xmin + 6, max(0, ymin - badge_h) + 4), status_label, fill=(255, 255, 255, 255))

            # Sub-badges for individual PPE items
            ppe_status_str = f"Helmet: {'OK' if has_hardhat else 'MISSING'} | Vest: {'OK' if has_vest else 'MISSING'}"
            draw.rectangle([xmin, ymax, xmin + len(ppe_status_str)*7 + 10, ymax + 18], fill=(30, 41, 59, 220))
            draw.text((xmin + 4, ymax + 2), ppe_status_str, fill=(255, 255, 255, 255))

    safety_score = round((compliant_workers / total_workers * 100), 1) if total_workers > 0 else 100.0

    summary = {
        "total_workers": total_workers,
        "compliant_workers": compliant_workers,
        "violation_count": len(violations),
        "safety_score": safety_score,
        "violations": violations
    }

    return img_draw, summary

def analyze_structural_crack(image: Image.Image) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Analyze surface defects, cracks, and fissures in concrete/masonry using OpenCV.
    Calculates crack contour length, estimated width (mm), and severity.
    """
    cv_img = pil_to_cv2(image)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    
    # Pre-processing: Gaussian blur + Adaptive Thresholding for crack extraction
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 40, 140)
    
    # Morphological closing to bridge small gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    overlay = cv_img.copy()
    crack_contours = []
    total_crack_pixels = 0
    max_crack_length = 0.0

    h, w = gray.shape

    for cnt in contours:
        area = cv2.contourArea(cnt)
        arc_len = cv2.arcLength(cnt, False)
        if arc_len > 40: # Filter noise
            crack_contours.append(cnt)
            total_crack_pixels += area
            if arc_len > max_crack_length:
                max_crack_length = arc_len

    # Draw highlighted crack paths in vibrant amber/red
    cv2.drawContours(overlay, crack_contours, -1, (0, 0, 255), 2)

    # Estimate physical dimensions based on assumed 0.2mm per pixel reference scale
    scale_mm_per_px = 0.25
    estimated_max_length_mm = round(max_crack_length * scale_mm_per_px, 1)
    estimated_width_mm = round(min(5.0, (total_crack_pixels / (max_crack_length + 1e-5)) * scale_mm_per_px * 0.4), 2)
    
    # Severity classification based on ACI 224R (Control of Cracking in Concrete Structures)
    if estimated_width_mm < 0.4:
        severity = "LOW (Hairline Shrinkage)"
        risk_color = "#10B981"
        action = "Monitor during scheduled bi-weekly inspections. No immediate structural intervention required."
    elif estimated_width_mm <= 1.5:
        severity = "MODERATE (Active Surface Fissure)"
        risk_color = "#F59E0B"
        action = "Apply epoxy resin surface injection and install displacement monitoring gauge pins."
    else:
        severity = "CRITICAL (Structural Shear Breach)"
        risk_color = "#EF4444"
        action = "Immediate structural engineer review required. Shoring recommended; halt loading above this bay."

    result_img = cv2_to_pil(overlay)

    metrics = {
        "crack_detected": len(crack_contours) > 0,
        "contour_count": len(crack_contours),
        "estimated_max_length_mm": estimated_max_length_mm,
        "estimated_width_mm": estimated_width_mm,
        "severity": severity,
        "risk_color": risk_color,
        "action_recommendation": action
    }

    return result_img, metrics

def compute_visual_diff(img_baseline: Image.Image, img_actual: Image.Image) -> Image.Image:
    """
    Compute a visual delta overlay comparing baseline blueprint/milestone to actual site capture.
    Highlights new structural members in green and deviations in orange/red.
    """
    # Resize actual to baseline size
    img_actual_resized = img_actual.resize(img_baseline.size)
    cv_base = pil_to_cv2(img_baseline)
    cv_act = pil_to_cv2(img_actual_resized)

    gray_base = cv2.cvtColor(cv_base, cv2.COLOR_BGR2GRAY)
    gray_act = cv2.cvtColor(cv_act, cv2.COLOR_BGR2GRAY)

    # Absolute difference
    diff = cv2.absdiff(gray_base, gray_act)
    _, thresh = cv2.threshold(diff, 35, 255, cv2.THRESH_BINARY)
    
    # Colorize difference
    color_diff = cv_act.copy()
    color_diff[thresh > 0] = [0, 210, 255] # Yellow-orange overlay on modified areas

    # Blend 60% actual + 40% overlay
    blended = cv2.addWeighted(cv_act, 0.65, color_diff, 0.35, 0)
    return cv2_to_pil(blended)
