from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


def apply_paper_processing(
    image: Image.Image,
    seed: int = 2026,
) -> Image.Image:
    """
    Apply realistic paper and ink processing using OpenCV.

    The pipeline introduces:
    - fine paper grain
    - low-frequency paper variation
    - gentle illumination changes
    - subtle ink intensity variation
    - mild local contrast enhancement
    """

    rgb = np.array(image.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    height, width = bgr.shape[:2]

    rng = np.random.default_rng(seed)

    # ---------------------------------------------------------
    # 1. Fine paper grain
    # ---------------------------------------------------------

    fine_noise = rng.normal(
        0,
        1.8,
        (height, width),
    ).astype(np.float32)

    fine_noise = cv2.GaussianBlur(
        fine_noise,
        (3, 3),
        0.6,
    )

    # ---------------------------------------------------------
    # 2. Low-frequency paper variation
    # ---------------------------------------------------------

    low_noise = rng.normal(
        0,
        1.0,
        (height, width),
    ).astype(np.float32)

    low_noise = cv2.GaussianBlur(
        low_noise,
        (0, 0),
        18,
    )

    low_noise = cv2.normalize(
        low_noise,
        None,
        -1,
        1,
        cv2.NORM_MINMAX,
    )

    # ---------------------------------------------------------
    # 3. Gentle illumination gradient
    # ---------------------------------------------------------

    yy, xx = np.mgrid[
        0:height,
        0:width
    ].astype(np.float32)

    cx = width * 0.5
    cy = height * 0.45

    distance = np.sqrt(
        ((xx - cx) / width) ** 2
        + ((yy - cy) / height) ** 2
    )

    illumination = np.clip(
        distance * 2.5,
        0,
        1,
    )

    # ---------------------------------------------------------
    # 4. Apply paper variation
    # ---------------------------------------------------------

    result = bgr.astype(np.float32)

    result += fine_noise[:, :, None] * 0.75
    result += low_noise[:, :, None] * 2.0
    result -= illumination[:, :, None] * 1.2

    # ---------------------------------------------------------
    # 5. Very subtle warm paper tone
    # ---------------------------------------------------------

    # BGR order.
    result[:, :, 0] -= 0.25
    result[:, :, 1] -= 0.10
    result[:, :, 2] += 0.30

    result = np.clip(
        result,
        0,
        255,
    ).astype(np.uint8)

    # ---------------------------------------------------------
    # 6. Local contrast enhancement
    # ---------------------------------------------------------

    lab = cv2.cvtColor(
        result,
        cv2.COLOR_BGR2LAB,
    )

    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=1.12,
        tileGridSize=(8, 8),
    )

    l_channel = clahe.apply(l_channel)

    enhanced = cv2.cvtColor(
        cv2.merge(
            (
                l_channel,
                a_channel,
                b_channel,
            )
        ),
        cv2.COLOR_LAB2BGR,
    )

    # ---------------------------------------------------------
    # 7. Preserve text while slightly softening digital edges
    # ---------------------------------------------------------

    blurred = cv2.GaussianBlur(
        enhanced,
        (3, 3),
        0.25,
    )

    # Blend mostly original with a small amount of smoothing.
    processed = cv2.addWeighted(
        enhanced,
        0.82,
        blurred,
        0.18,
        0,
    )

    # ---------------------------------------------------------
    # 8. Convert back to Pillow
    # ---------------------------------------------------------

    processed_rgb = cv2.cvtColor(
        processed,
        cv2.COLOR_BGR2RGB,
    )

    return Image.fromarray(processed_rgb)