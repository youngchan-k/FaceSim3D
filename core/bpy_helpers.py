"""
Low-level Blender helpers: object mode, selection, collections, origin.

Distinct from sample/utils/blender_utils.py.
"""
import bpy

from core.defs import FACE_COLLECTION_NAME


def ensure_object_mode() -> None:
    """Switch to OBJECT mode if not already."""
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def deselect_all() -> None:
    """OBJECT mode and deselect all."""
    ensure_object_mode()
    bpy.ops.object.select_all(action="DESELECT")


def get_face_collection():
    """Return the Face collection, creating it if missing."""
    col = bpy.data.collections.get(FACE_COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(FACE_COLLECTION_NAME)
        bpy.context.scene.collection.children.link(col)
    return col


def move_object_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    """Put object in the given collection and remove from others."""
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    for c in list(obj.users_collection):
        if c != collection:
            c.objects.unlink(obj)


def set_origin_to_geometry(obj: bpy.types.Object) -> None:
    """Set object origin to geometry bounds center."""
    ensure_object_mode()
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
