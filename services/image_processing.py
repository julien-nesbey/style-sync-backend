from __future__ import annotations

import base64
import io
from collections import Counter

import numpy as np
from PIL import Image
from rembg import remove
from sklearn.cluster import KMeans

from models.schemas import DominantColor


COLOR_LOOKUP: dict[str, tuple[int, int, int]] = {
    "Navy Blue": (32, 42, 68),
    "Warm Beige": (201, 173, 136),
    "Olive Green": (107, 123, 76),
    "Charcoal": (54, 69, 79),
    "Cream": (244, 236, 220),
    "Burgundy": (128, 32, 64),
    "Sky Blue": (115, 189, 244),
    "Jet Black": (18, 18, 18),
    "Snow White": (245, 245, 245),
    "Terracotta": (198, 110, 70),
}


class ImageService:
    """ML-backed image pipeline for clean photos and accessible color insights."""

    @staticmethod
    def remove_background(image_bytes: bytes) -> bytes:
        """Use rembg to isolate the garment from noisy backgrounds."""

        return remove(image_bytes) # type: ignore

    @staticmethod
    def extract_dominant_colors(image_bytes: bytes, n_colors: int = 3) -> list[DominantColor]:
        """Run K-Means over garment pixels to identify dominant colors.

        The clustering step transforms raw pixels into centroids that represent the
        key tones of the item, which powers matching and analytics in the app.
        """

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        pixels = np.array(image).reshape(-1, 3)

        # Ignore near-transparent/near-white leftovers from segmentation artifacts.
        mask = np.any(pixels < 245, axis=1)
        filtered = pixels[mask]
        if filtered.size == 0:
            filtered = pixels

        # Keep ML latency predictable on mobile uploads.
        max_samples = 10000
        if len(filtered) > max_samples:
            rng = np.random.default_rng(seed=42)
            idx = rng.choice(len(filtered), size=max_samples, replace=False)
            filtered = filtered[idx]

        clusters = max(1, min(n_colors, len(filtered)))
        kmeans = KMeans(n_clusters=clusters, n_init="auto", random_state=42)
        labels = kmeans.fit_predict(filtered)
        centroids = np.clip(kmeans.cluster_centers_, 0, 255).astype(int)

        counts = Counter(labels)
        total = sum(counts.values())

        dominant: list[DominantColor] = []
        for cluster_id, count in counts.most_common():
            centroid = centroids[cluster_id]
            rgb = (int(centroid[0]), int(centroid[1]), int(centroid[2]))
            dominant.append(
                DominantColor(
                    hex=ImageService.rgb_to_hex(rgb),
                    name=ImageService.closest_color_name(rgb),
                    ratio=round(count / total, 4),
                )
            )

        return dominant

    @staticmethod
    def closest_color_name(rgb: tuple[int, int, int]) -> str:
        """Map RGB values to the nearest named color for color-blind accessibility."""

        def distance(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
            return float(np.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2))))

        return min(COLOR_LOOKUP, key=lambda name: distance(rgb, COLOR_LOOKUP[name]))

    @staticmethod
    def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

    @staticmethod
    def to_base64_png(image_bytes: bytes) -> str:
        """Encode binary PNG payload for API responses consumed by React Native."""

        return base64.b64encode(image_bytes).decode("utf-8")

    @staticmethod
    def describe_pair(top_color: DominantColor, bottom_color: DominantColor) -> str:
        """Generate a readable sentence used by Color Blind Mode in the app."""

        return (
            f"This outfit pairs a {top_color.name} top with {bottom_color.name} bottoms."
        )
