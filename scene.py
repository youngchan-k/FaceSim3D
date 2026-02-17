"""Scene setup: mesh import, materials, eye tracking, cameras."""
import math
import os
import re

import bpy
from mathutils import Euler, Vector

from cfg import (
    EYE_BASE,
    EYE_LEFT,
    EYE_RIGHT,
    OBJ_FILES,
    TARGET_OBJ,
    TARGET_POS,
    TARGET_SCALE,
    TRACK_AXIS,
    UP_AXIS,
    Config,
    FACE_COL,
)


def _obj_mode():
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def _deselect():
    _obj_mode()
    bpy.ops.object.select_all(action="DESELECT")


def get_face_collection():
    col = bpy.data.collections.get(FACE_COL)
    if col is None:
        col = bpy.data.collections.new(FACE_COL)
        bpy.context.scene.collection.children.link(col)
    return col


def _move_to_collection(obj, col):
    if obj.name not in col.objects:
        col.objects.link(obj)
    for c in list(obj.users_collection):
        if c != col:
            c.objects.unlink(obj)


def _origin_to_geom(obj):
    _obj_mode()
    _deselect()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")


def _strip_suffix(name: str) -> str:
    return re.sub(r"\.\d{3}$", "", name).strip()


def _mesh_center_x(obj) -> float:
    mw = obj.matrix_world
    verts = obj.data.vertices
    return sum((mw @ v.co).x for v in verts) / len(verts) if verts else obj.location.x


def _import_obj(path: str):
    try:
        bpy.ops.wm.obj_import(filepath=path)
    except Exception:
        bpy.ops.import_scene.obj(filepath=path)


def check_paths(cfg: Config) -> list[str]:
    paths = [os.path.join(cfg.obj_dir, f) for f in OBJ_FILES]
    missing = [p for p in paths if not os.path.isfile(p)]
    if missing:
        raise FileNotFoundError("Missing:\n" + "\n".join(missing))
    return paths


def load_meshes(paths: list[str], face_col) -> None:
    before = set(bpy.data.objects)
    for path in paths:
        _obj_mode()
        _import_obj(path)
        after = set(bpy.data.objects)
        for obj in after - before:
            if obj.type != "MESH":
                continue
            _move_to_collection(obj, face_col)
            if obj.name in {"Head", "Eye Lens"}:
                _deselect()
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.shade_auto_smooth(angle=math.radians(180))
        before = after


def split_eyes(face_col) -> tuple:
    eyes = [o for o in face_col.objects if o.type == "MESH" and _strip_suffix(o.name) == EYE_BASE]
    if len(eyes) == 1:
        _obj_mode()
        _deselect()
        eyes[0].select_set(True)
        bpy.context.view_layer.objects.active = eyes[0]
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.separate(type="LOOSE")
        bpy.ops.object.mode_set(mode="OBJECT")

    candidates = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(EYE_BASE)]
    candidates = [o for o in candidates if face_col in o.users_collection] or candidates
    candidates.sort(key=_mesh_center_x)
    if len(candidates) < 2:
        raise RuntimeError("Could not split Eye Lens into left/right")

    left, right = candidates[0], candidates[-1]
    left.name = left.data.name = EYE_LEFT
    right.name = right.data.name = EYE_RIGHT
    _move_to_collection(left, face_col)
    _move_to_collection(right, face_col)
    return left, right


def _visual_to_optical(visual: Vector, eye_pos: Vector, kh: float, kv: float, left: bool) -> Vector:
    d = (visual - eye_pos).length
    if d < 1e-6:
        return visual
    vd = (visual - eye_pos) / d
    up = Vector((0, 0, 1))
    right = vd.cross(up)
    if right.length < 0.1:
        right = Vector((1, 0, 0))
    right.normalize()
    up_p = right.cross(vd)
    up_p.normalize()
    hoff = (-d * math.tan(kh) if left else d * math.tan(kh))
    voff = -d * math.tan(kv)
    return visual + right * hoff + up_p * voff


def make_target(face_col):
    _obj_mode()
    cube = bpy.data.objects.get(TARGET_OBJ)
    if cube is None:
        bpy.ops.mesh.primitive_cube_add(location=TARGET_POS)
        cube = bpy.context.active_object
        cube.name = TARGET_OBJ
    else:
        cube.location = TARGET_POS
    cube.scale = TARGET_SCALE
    for c in list(cube.users_collection):
        if c == face_col:
            c.objects.unlink(cube)
    return cube


def setup_eye_tracking(eyes: tuple, cfg: Config) -> None:
    left, right = eyes
    for o in eyes:
        _origin_to_geom(o)

    kh = math.radians(cfg.kappa_angle_horizontal)
    kv = math.radians(cfg.kappa_angle_vertical)
    vt = Vector(cfg.target_location)

    lo = _visual_to_optical(vt, Vector(left.location), kh, kv, True)
    ro = _visual_to_optical(vt, Vector(right.location), kh, kv, False)

    def ensure_empty(name, loc):
        o = bpy.data.objects.get(name)
        if o is None:
            bpy.ops.object.empty_add(type="PLAIN_AXES", location=loc)
            o = bpy.context.active_object
            o.name = name
        else:
            o.location = loc
        return o

    lopt = ensure_empty(f"{TARGET_OBJ}_Left_Optical", lo)
    ropt = ensure_empty(f"{TARGET_OBJ}_Right_Optical", ro)

    for eye, opt in [(left, lopt), (right, ropt)]:
        c = eye.constraints.get("TrackTo_Target") or eye.constraints.new("TRACK_TO")
        c.name = "TrackTo_Target"
        c.target = opt
        c.track_axis = TRACK_AXIS
        c.up_axis = UP_AXIS

    lk = ensure_empty(f"{TARGET_OBJ}_Left_Kappa", left.location)
    rk = ensure_empty(f"{TARGET_OBJ}_Right_Kappa", right.location)
    for o in (lk, rk):
        o.rotation_mode = "QUATERNION"
    lk.rotation_quaternion = Euler((kv, 0, kh), "XYZ").to_quaternion()
    rk.rotation_quaternion = Euler((kv, 0, -kh), "XYZ").to_quaternion()

    for eye, k in [(left, lk), (right, rk)]:
        c = eye.constraints.get("Kappa_Offset") or eye.constraints.new("COPY_ROTATION")
        c.name = "Kappa_Offset"
        c.target = k
        c.use_x, c.use_y, c.use_z = True, False, True
        c.mix_mode = "ADD"
        c.influence = 1.0


def move_target(cfg: Config) -> None:
    t = bpy.data.objects.get(TARGET_OBJ)
    if t is None:
        raise RuntimeError("Target not found")
    t.location = cfg.target_location

    le = bpy.data.objects.get(EYE_LEFT)
    re = bpy.data.objects.get(EYE_RIGHT)
    lo = bpy.data.objects.get(f"{TARGET_OBJ}_Left_Optical")
    ro = bpy.data.objects.get(f"{TARGET_OBJ}_Right_Optical")
    if not all((le, re, lo, ro)):
        return

    vt = Vector(cfg.target_location)
    kh = math.radians(cfg.kappa_angle_horizontal)
    kv = math.radians(cfg.kappa_angle_vertical)
    lo.location = _visual_to_optical(vt, Vector(le.location), kh, kv, True)
    ro.location = _visual_to_optical(vt, Vector(re.location), kh, kv, False)


def _set_img(node, path: str, colorspace: str | None = None):
    img = bpy.data.images.load(path, check_existing=True)
    node.image = img
    if colorspace:
        node.image.colorspace_settings.name = colorspace


def assign_mats() -> None:
    m = {"Head": ["Head"], "Lashes": ["Lashes"], "Eye_Lens": [EYE_LEFT, EYE_RIGHT], "Teeth": ["Teeth"]}
    for mat_name, obj_names in m.items():
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
    head = bpy.data.objects.get("Head")
    nt = head.active_material.node_tree
    td = cfg.tex_dir
    _set_img(nt.nodes.get("Color"), os.path.join(td, "Colour_8k.jpg"))
    _set_img(nt.nodes.get("Gloss"), os.path.join(td, "Gloss.jpg"), "Non-Color")
    _set_img(nt.nodes.get("Spec"), os.path.join(td, "Spec.jpg"), "Non-Color")

    for en in (EYE_LEFT, EYE_RIGHT):
        eye = bpy.data.objects.get(en)
        if eye is None:
            raise RuntimeError(f"Object not found: {en}")
        nt = eye.active_material.node_tree
        ed = cfg.eye_tex_dir
        _set_img(nt.nodes.get("Image Texture"), os.path.join(ed, "Eye Colour.jpg"))
        pb = nt.nodes.get("Principled BSDF")
        if pb:
            pb.inputs["IOR"].default_value = cfg.eye_ior

    teeth = bpy.data.objects.get("Teeth")
    _set_img(teeth.active_material.node_tree.nodes.get("Image Texture"), os.path.join(td, "Teeth.jpg"))


def load_hdri(cfg: Config) -> None:
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


def skin_curve(cfg: Config) -> None:
    head = bpy.data.objects.get("Head")
    mapping = head.active_material.node_tree.nodes.get("RGB Curves").mapping
    pts = mapping.curves[3].points
    while len(pts) > 2:
        pts.remove(pts[len(pts) - 2])
    pts[0].location = (0, 0)
    pts[-1].location = (1, 1)
    if len(pts) <= 2:
        pts.new(cfg.curve_x, cfg.curve_y)
    else:
        min(pts, key=lambda p: abs(p.location[0] - cfg.curve_x)).location = (cfg.curve_x, cfg.curve_y)
    mapping.update()


def setup_cameras(cfg: Config) -> None:
    left = bpy.data.objects.get("Left")
    right = bpy.data.objects.get("Right")
    if not left or not right:
        return
    for cam in (left, right):
        d = getattr(cam, "data", None)
        if d:
            d.lens = cfg.cam_focal_length_mm
            d.sensor_width = cfg.cam_sensor_width_mm
            d.sensor_height = cfg.cam_sensor_height_mm
    rad = tuple(math.radians(r) for r in cfg.cam_rotation)
    left.rotation_euler = rad
    left.rotation_euler[2] = -left.rotation_euler[2]
    right.rotation_euler = rad


def setup_glasses(cfg: Config) -> None:
    g = bpy.data.objects.get("Glasses")
    if g is None:
        return
    g.location = cfg.glasses_location
    g.rotation_euler = tuple(math.radians(r) for r in cfg.glasses_rotation)
    g.scale = cfg.glasses_scale
