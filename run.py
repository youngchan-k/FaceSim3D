"""Entry point: load scene, setup, render, save."""
import bpy

from cfg import Config, TEMPLATE, save_params
from export import render_stereo, save_blend
from scene import (
    assign_mats,
    check_paths,
    get_face_collection,
    load_hdri,
    load_meshes,
    load_textures,
    make_target,
    move_target,
    setup_cameras,
    setup_eye_tracking,
    setup_glasses,
    skin_curve,
    split_eyes,
)


def main():
    cfg = Config()
    bpy.ops.wm.open_mainfile(filepath=TEMPLATE)
    paths = check_paths(cfg)

    face = get_face_collection()
    load_meshes(paths, face)
    left, right = split_eyes(face)
    make_target(face)
    setup_eye_tracking((left, right), cfg)

    assign_mats()
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
