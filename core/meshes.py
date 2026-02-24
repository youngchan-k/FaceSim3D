"""
OBJ validation, import, and eye split. Distinct from sample/utils/mesh_import.py.
"""
import math
import os
import re

import bpy

from core.bpy_helpers import (
    deselect_all,
    ensure_object_mode,
    move_object_to_collection,
)
from core.defs import (
    EYE_BASE_NAME,
    EYE_LEFT_NAME,
    EYE_NEW_OBJ_FILENAME,
    EYE_RIGHT_NAME,
    EYES_DIR,
    OBJ_FILES,
    OBJ_FILES_SEPARATE_EYES,
)
from core.settings import Config


def _strip_blender_suffix(name: str) -> str:
    """Remove Blender numeric suffix (e.g. .001) from object name."""
    return re.sub(r"\.\d{3}$", "", name).strip()


def _mesh_center_x(obj: bpy.types.Object) -> float:
    """World-space X of mesh centroid; used to order left/right eyes."""
    verts = obj.data.vertices
    if not verts:
        return obj.location.x
    mw = obj.matrix_world
    return sum((mw @ v.co).x for v in verts) / len(verts)


def _import_obj(filepath: str) -> None:
    """Import one OBJ (modern API with legacy fallback)."""
    try:
        bpy.ops.wm.obj_import(filepath=filepath)
    except Exception:
        bpy.ops.import_scene.obj(filepath=filepath)


def check_paths(cfg: Config) -> list[str]:
    """
    Verify required OBJ files exist; return their paths.
    When use_common_eye_mesh=True: all from cfg.obj_dir (OBJ_FILES).
    When False: Head/Lashes/Teeth from cfg.obj_dir; eye_lens.OBJ from EYES_DIR (data/eyes), listed twice.
    Raises FileNotFoundError if any file is missing.
    """
    if cfg.use_common_eye_mesh:
        paths = [os.path.join(cfg.obj_dir, f) for f in OBJ_FILES]
    else:
        paths = [os.path.join(cfg.obj_dir, f) for f in OBJ_FILES_SEPARATE_EYES]
        eye_path = os.path.join(EYES_DIR, EYE_NEW_OBJ_FILENAME)
        paths.extend([eye_path, eye_path])
    missing = [p for p in paths if not os.path.isfile(p)]
    if missing:
        raise FileNotFoundError("Missing:\n" + "\n".join(missing))
    return paths


def load_meshes(paths: list[str], face_col: bpy.types.Collection, cfg: Config) -> None:
    """
    Import OBJs into Face collection; auto-smooth Head and eyes as needed.
    When use_common_eye_mesh=True: smooth Head and "Eye Lens".
    When False: import eye_lens.OBJ from data/eyes twice (first=left, second=right), name and smooth each.
    """
    before = set(bpy.data.objects)
    for path in paths:
        ensure_object_mode()
        _import_obj(path)
        after = set(bpy.data.objects)
        basename = os.path.basename(path)
        for obj in after - before:
            if obj.type != "MESH":
                continue
            if not cfg.use_common_eye_mesh and basename == EYE_NEW_OBJ_FILENAME:
                if bpy.data.objects.get(EYE_LEFT_NAME) is None:
                    obj.name = obj.data.name = EYE_LEFT_NAME
                else:
                    obj.name = obj.data.name = EYE_RIGHT_NAME
            move_object_to_collection(obj, face_col)
            needs_smooth = (
                obj.name == "Head"
                or (cfg.use_common_eye_mesh and obj.name == "Eye Lens")
                or (not cfg.use_common_eye_mesh and obj.name in (EYE_LEFT_NAME, EYE_RIGHT_NAME))
            )
            if needs_smooth:
                deselect_all()
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.shade_auto_smooth(angle=math.radians(180))
        before = after


def split_eyes(face_col: bpy.types.Collection, cfg: Config) -> tuple[bpy.types.Object, bpy.types.Object]:
    """
    Return (left_eye, right_eye) for the pipeline.
    When use_common_eye_mesh=True: split combined "Eye Lens" by loose parts, name by X, return.
    When False: left/right already exist (mesh imported twice); apply eye_*_location and eye_*_scale, return.
    """
    if not cfg.use_common_eye_mesh:
        left = bpy.data.objects.get(EYE_LEFT_NAME)
        right = bpy.data.objects.get(EYE_RIGHT_NAME)
        if left is None or right is None:
            raise RuntimeError(
                "Separate eye mode: expected '%s' and '%s'. "
                "Ensure %s is in data/eyes/ and imported twice."
                % (EYE_LEFT_NAME, EYE_RIGHT_NAME, EYE_NEW_OBJ_FILENAME)
            )
        left.location = cfg.eye_left_location
        left.scale = cfg.eye_left_scale
        right.location = cfg.eye_right_location
        right.scale = cfg.eye_right_scale
        return left, right

    eyes = [
        o
        for o in face_col.objects
        if o.type == "MESH" and _strip_blender_suffix(o.name) == EYE_BASE_NAME
    ]
    if len(eyes) == 1:
        ensure_object_mode()
        deselect_all()
        eyes[0].select_set(True)
        bpy.context.view_layer.objects.active = eyes[0]
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.separate(type="LOOSE")
        bpy.ops.object.mode_set(mode="OBJECT")

    candidates = [
        o
        for o in bpy.data.objects
        if o.type == "MESH" and o.name.startswith(EYE_BASE_NAME)
    ]
    in_face = [o for o in candidates if face_col in o.users_collection]
    candidates = in_face if in_face else candidates
    candidates.sort(key=_mesh_center_x)
    if len(candidates) < 2:
        raise RuntimeError("Could not split Eye Lens into left/right")

    left, right = candidates[0], candidates[-1]
    left.name = left.data.name = EYE_LEFT_NAME
    right.name = right.data.name = EYE_RIGHT_NAME
    move_object_to_collection(left, face_col)
    move_object_to_collection(right, face_col)
    return left, right
