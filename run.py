"""
Entry point for the face rendering pipeline.
Run from Blender: blender --background --python run.py
"""
import bpy

from config.defs import TEMPLATE_PATH
from config.settings import Config, save_params
from bpy_utils.helpers import get_face_collection
from mesh.meshes import check_paths, load_meshes, split_eyes
from scene.gaze import (
    make_target,
    move_target,
    setup_cameras,
    setup_eye_tracking,
    setup_glasses,
    skin_curve,
)
from materials.textures import assign_materials, load_hdri, load_textures
from export.render import render_stereo, save_blend


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
