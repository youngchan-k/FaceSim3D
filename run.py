"""
Entry point for the face rendering pipeline.

Run from Blender (Scripting or CLI: blender template.blend --background --python run.py).
Uses the core package (distinct from sample/: sample has main.py + utils/, this uses run.py + core/).

Pipeline: load template → validate paths → import meshes → split eyes → target & eye tracking
→ assign materials & load textures & HDRI → target/skin/cameras/glasses → render stereo → save blend & config.
"""
import bpy

from core.bpy_helpers import get_face_collection
from core.export import render_stereo, save_blend
from core.gaze import (
    make_target,
    move_target,
    setup_cameras,
    setup_eye_tracking,
    setup_glasses,
    skin_curve,
)
from core.meshes import check_paths, load_meshes, split_eyes
from core.defs import TEMPLATE_PATH
from core.settings import Config, save_params
from core.textures import assign_materials, load_hdri, load_textures


def main() -> None:
    """Run the full pipeline: load scene, import assets, materials & gaze, render, save."""
    cfg = Config()
    bpy.ops.wm.open_mainfile(filepath=TEMPLATE_PATH)
    paths = check_paths(cfg)

    face_col = get_face_collection()
    load_meshes(paths, face_col, cfg)
    left_eye, right_eye = split_eyes(face_col, cfg)
    make_target(face_col)
    setup_eye_tracking(left_eye, right_eye, cfg)

    assign_materials()
    load_textures(cfg)
    load_hdri(cfg)

    move_target(cfg)
    skin_curve(cfg)
    setup_cameras(cfg)
    setup_glasses(cfg)

    render_stereo(cfg)
    save_blend(cfg)
    save_params(cfg)


if __name__ == "__main__":
    main()
