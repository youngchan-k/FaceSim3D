"""Target, eye tracking (kappa), cameras, glasses, skin curve."""
import math

import bpy
from mathutils import Euler, Vector

from bpy_utils.helpers import ensure_object_mode, set_origin_to_geometry
from config.defs import (
    CAMERA_LEFT_NAME,
    CAMERA_RIGHT_NAME,
    EYE_LEFT_NAME,
    EYE_RIGHT_NAME,
    GLASSES_OBJECT_NAME,
    TARGET_INIT_LOCATION,
    TARGET_OBJECT_NAME,
    TARGET_SCALE,
    TRACK_AXIS,
    UP_AXIS,
)
from config.settings import Config


def _visual_to_optical_target(
    visual_target: Vector,
    eye_position: Vector,
    kappa_horizontal_rad: float,
    kappa_vertical_rad: float,
    is_left_eye: bool,
) -> Vector:
    """Compute optical-axis target from visual target and kappa angles."""
    d = (visual_target - eye_position).length
    if d < 1e-6:
        return visual_target
    vd = (visual_target - eye_position) / d
    up = Vector((0, 0, 1))
    right = vd.cross(up)
    if right.length < 0.1:
        right = Vector((1, 0, 0))
    right.normalize()
    up_plane = right.cross(vd)
    up_plane.normalize()
    h_off = -d * math.tan(kappa_horizontal_rad) if is_left_eye else d * math.tan(kappa_horizontal_rad)
    v_off = -d * math.tan(kappa_vertical_rad)
    return visual_target + right * h_off + up_plane * v_off


def make_target(face_col: bpy.types.Collection) -> bpy.types.Object:
    """Create or reset Target cube; unlink from Face collection."""
    ensure_object_mode()
    cube = bpy.data.objects.get(TARGET_OBJECT_NAME)
    if cube is None:
        bpy.ops.mesh.primitive_cube_add(location=TARGET_INIT_LOCATION)
        cube = bpy.context.active_object
        cube.name = TARGET_OBJECT_NAME
    else:
        cube.location = TARGET_INIT_LOCATION
    cube.scale = TARGET_SCALE
    for c in list(cube.users_collection):
        if c == face_col:
            c.objects.unlink(cube)
    return cube


def setup_eye_tracking(
    left_eye: bpy.types.Object,
    right_eye: bpy.types.Object,
    cfg: Config,
) -> None:
    """Set up TRACK_TO and kappa COPY_ROTATION so eyes look at visual target."""
    for obj in (left_eye, right_eye):
        set_origin_to_geometry(obj)

    kh = math.radians(cfg.kappa_angle_horizontal)
    kv = math.radians(cfg.kappa_angle_vertical)
    vt = Vector(cfg.target_location)
    lo_pos = _visual_to_optical_target(vt, Vector(left_eye.location), kh, kv, True)
    ro_pos = _visual_to_optical_target(vt, Vector(right_eye.location), kh, kv, False)

    def ensure_empty(name: str, location: Vector) -> bpy.types.Object:
        o = bpy.data.objects.get(name)
        if o is None:
            bpy.ops.object.empty_add(type="PLAIN_AXES", location=location)
            o = bpy.context.active_object
            o.name = name
        else:
            o.location = location
        return o

    left_optical = ensure_empty(f"{TARGET_OBJECT_NAME}_Left_Optical", lo_pos)
    right_optical = ensure_empty(f"{TARGET_OBJECT_NAME}_Right_Optical", ro_pos)
    for eye, opt in [(left_eye, left_optical), (right_eye, right_optical)]:
        c = eye.constraints.get("TrackTo_Target") or eye.constraints.new("TRACK_TO")
        c.name = "TrackTo_Target"
        c.target = opt
        c.track_axis = TRACK_AXIS
        c.up_axis = UP_AXIS

    left_kappa = ensure_empty(f"{TARGET_OBJECT_NAME}_Left_Kappa", left_eye.location)
    right_kappa = ensure_empty(f"{TARGET_OBJECT_NAME}_Right_Kappa", right_eye.location)
    for o in (left_kappa, right_kappa):
        o.rotation_mode = "QUATERNION"
    left_kappa.rotation_quaternion = Euler((kv, 0, kh), "XYZ").to_quaternion()
    right_kappa.rotation_quaternion = Euler((kv, 0, -kh), "XYZ").to_quaternion()
    for eye, k in [(left_eye, left_kappa), (right_eye, right_kappa)]:
        c = eye.constraints.get("Kappa_Offset") or eye.constraints.new("COPY_ROTATION")
        c.name = "Kappa_Offset"
        c.target = k
        c.use_x, c.use_y, c.use_z = True, False, True
        c.mix_mode = "ADD"
        c.influence = 1.0


def move_target(cfg: Config) -> None:
    """Update Target and optical empties to cfg.target_location and kappa."""
    t = bpy.data.objects.get(TARGET_OBJECT_NAME)
    if t is None:
        raise RuntimeError("Target not found")
    t.location = cfg.target_location
    left_eye = bpy.data.objects.get(EYE_LEFT_NAME)
    right_eye = bpy.data.objects.get(EYE_RIGHT_NAME)
    left_opt = bpy.data.objects.get(f"{TARGET_OBJECT_NAME}_Left_Optical")
    right_opt = bpy.data.objects.get(f"{TARGET_OBJECT_NAME}_Right_Optical")
    if not all((left_eye, right_eye, left_opt, right_opt)):
        return
    vt = Vector(cfg.target_location)
    kh = math.radians(cfg.kappa_angle_horizontal)
    kv = math.radians(cfg.kappa_angle_vertical)
    left_opt.location = _visual_to_optical_target(vt, Vector(left_eye.location), kh, kv, True)
    right_opt.location = _visual_to_optical_target(vt, Vector(right_eye.location), kh, kv, False)


def skin_curve(cfg: Config) -> None:
    """Set head RGB Curves control point to (curve_x, curve_y)."""
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
    """Apply lens, sensor, and rotation to Left/Right cameras."""
    left = bpy.data.objects.get(CAMERA_LEFT_NAME)
    right = bpy.data.objects.get(CAMERA_RIGHT_NAME)
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
    """Set Glasses object location, rotation, scale from config."""
    g = bpy.data.objects.get(GLASSES_OBJECT_NAME)
    if g is None:
        return
    g.location = cfg.glasses_location
    g.rotation_euler = tuple(math.radians(r) for r in cfg.glasses_rotation)
    g.scale = cfg.glasses_scale
