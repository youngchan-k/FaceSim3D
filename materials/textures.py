"""Material assignment, texture and HDRI loading."""
import math
import os

import bpy

from config.defs import EYE_LEFT_NAME, EYE_RIGHT_NAME
from config.settings import Config


def _set_image_on_node(
    node: bpy.types.Node,
    filepath: str,
    colorspace: str | None = None,
) -> None:
    """Load image into node; optionally set colorspace."""
    img = bpy.data.images.load(filepath, check_existing=True)
    node.image = img
    if colorspace:
        node.image.colorspace_settings.name = colorspace


def assign_materials() -> None:
    """Assign template materials Head, Lashes, Eye_Lens, Teeth to corresponding objects."""
    mapping = {
        "Head": ["Head"],
        "Lashes": ["Lashes"],
        "Eye_Lens": [EYE_LEFT_NAME, EYE_RIGHT_NAME],
        "Teeth": ["Teeth"],
    }
    for mat_name, obj_names in mapping.items():
        mat = bpy.data.materials.get(mat_name)
        if mat is None:
            raise RuntimeError(f"Material not found: {mat_name}")
        for on in obj_names:
            obj = bpy.data.objects.get(on)
            if obj is None:
                raise RuntimeError(f"Object not found: {on}")
            obj.data.materials.clear()
            obj.data.materials.append(mat)


def load_textures(cfg: Config) -> None:
    """Load head/eye/teeth textures and set eye IOR from config paths."""
    head = bpy.data.objects.get("Head")
    nt = head.active_material.node_tree
    td = cfg.tex_dir
    _set_image_on_node(nt.nodes.get("Color"), os.path.join(td, "Colour_8k.jpg"))
    _set_image_on_node(nt.nodes.get("Gloss"), os.path.join(td, "Gloss.jpg"), "Non-Color")
    _set_image_on_node(nt.nodes.get("Spec"), os.path.join(td, "Spec.jpg"), "Non-Color")
    for en in (EYE_LEFT_NAME, EYE_RIGHT_NAME):
        eye = bpy.data.objects.get(en)
        if eye is None:
            raise RuntimeError(f"Object not found: {en}")
        nt = eye.active_material.node_tree
        ed = cfg.eye_tex_dir
        _set_image_on_node(nt.nodes.get("Image Texture"), os.path.join(ed, "Eye Colour.jpg"))
        pb = nt.nodes.get("Principled BSDF")
        if pb:
            pb.inputs["IOR"].default_value = cfg.eye_ior
    teeth = bpy.data.objects.get("Teeth")
    _set_image_on_node(
        teeth.active_material.node_tree.nodes.get("Image Texture"),
        os.path.join(td, "Teeth.jpg"),
    )


def load_hdri(cfg: Config) -> None:
    """Load HDRI into world; set Mapping Z rotation and Background strength."""
    img = bpy.data.images.load(cfg.hdri_path, check_existing=True)
    scene = bpy.context.scene
    wt = scene.world.node_tree
    nodes = wt.nodes
    nodes.get("Environment Texture").image = img
    m = nodes.get("Mapping")
    r = m.inputs["Rotation"].default_value
    r[2] = math.radians(cfg.hdri_z_rot_deg)
    m.inputs["Rotation"].default_value = r
    nodes.get("Background").inputs["Strength"].default_value = cfg.hdri_brightness
    wt.update_tag()
    bpy.context.view_layer.update()
