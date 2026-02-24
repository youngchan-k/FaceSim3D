"""
Stereo render and blend save. Distinct from sample/utils/rendering.py.
"""
import os
import shutil

import bpy

from core.defs import (
    CAMERA_LEFT_NAME,
    CAMERA_RIGHT_NAME,
    DEFAULT_BLEND_FILENAME,
    RENDER_OUTPUT_LEFT,
    RENDER_OUTPUT_RIGHT,
)
from core.settings import Config


def _apply_render_settings(cfg: Config) -> None:
    """Set Cycles engine, samples, resolution, device; enable GPU if requested."""
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.samples = cfg.render_samples
    s.render.resolution_x = cfg.render_resolution_x
    s.render.resolution_y = cfg.render_resolution_y
    s.cycles.device = cfg.render_device
    if cfg.render_device == "GPU":
        try:
            for d in bpy.context.preferences.addons["cycles"].preferences.devices:
                if d.type in ("OPTIX", "CUDA", "OPENCL", "METAL"):
                    d.use = True
        except (KeyError, AttributeError):
            pass


def render_stereo(cfg: Config) -> None:
    """Render Left and Right cameras to view_L.png and view_R.png in save_dir."""
    _apply_render_settings(cfg)
    os.makedirs(cfg.save_dir, exist_ok=True)
    s = bpy.context.scene
    r = s.render
    for cam_name, out_name in [
        (CAMERA_LEFT_NAME, RENDER_OUTPUT_LEFT),
        (CAMERA_RIGHT_NAME, RENDER_OUTPUT_RIGHT),
    ]:
        cam = bpy.data.objects.get(cam_name)
        if cam:
            s.camera = cam
            r.filepath = os.path.join(cfg.save_dir, out_name)
            bpy.ops.render.render(write_still=True)


def save_blend(
    cfg: Config,
    filename: str | None = None,
    pack: bool = True,
) -> str:
    """Save scene to .blend in save_dir; optionally pack external images."""
    filename = filename or DEFAULT_BLEND_FILENAME
    os.makedirs(cfg.save_dir, exist_ok=True)
    path = os.path.join(cfg.save_dir, filename)
    bpy.ops.wm.save_as_mainfile(filepath=path, check_existing=False, compress=True)

    if pack:
        assets = os.path.join(cfg.save_dir, "assets")
        os.makedirs(assets, exist_ok=True)
        to_remove = []
        for img in bpy.data.images:
            if img is None or img.packed_file or getattr(img, "source", None) != "FILE":
                continue
            src = getattr(img, "filepath", "") or ""
            if not src:
                continue
            try:
                ap = bpy.path.abspath(src)
            except Exception:
                ap = ""
            if ap and not os.path.isfile(ap) and getattr(img, "users", 0) == 0:
                to_remove.append(img)
        for img in to_remove:
            try:
                bpy.data.images.remove(img)
            except Exception:
                pass
        used = set()
        for img in bpy.data.images:
            if img is None or img.packed_file or getattr(img, "source", None) != "FILE":
                continue
            src = getattr(img, "filepath", "") or ""
            if not src:
                continue
            try:
                ap = bpy.path.abspath(src)
            except Exception:
                continue
            if not ap or not os.path.isfile(ap):
                continue
            base = os.path.basename(ap)
            name, ext = os.path.splitext(base)
            cand = base
            i = 1
            while cand in used or os.path.exists(os.path.join(assets, cand)):
                cand = f"{name}_{i}{ext}"
                i += 1
            used.add(cand)
            try:
                shutil.copy2(ap, os.path.join(assets, cand))
                img.filepath = f"//assets/{cand}"
            except Exception:
                pass
        for img in bpy.data.images:
            if img is None or img.packed_file or getattr(img, "source", None) != "FILE":
                continue
            src = getattr(img, "filepath", "") or ""
            if not src:
                continue
            try:
                ap = bpy.path.abspath(src)
            except Exception:
                ap = ""
            if ap and os.path.isfile(ap):
                try:
                    img.pack()
                except Exception:
                    pass
        bpy.ops.wm.save_as_mainfile(filepath=path, check_existing=False, compress=True)
        if os.path.isdir(assets):
            shutil.rmtree(assets)
    return path
