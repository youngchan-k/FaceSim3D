"""
Project-wide definitions: paths, asset names, and scene object identifiers.

Centralizes literal values used across the pipeline so file layout and
naming can be changed in one place. Distinct from sample/utils/constants.py.
"""
import os

# Project root is the directory that contains this package (core/)
_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT: str = os.path.dirname(_CORE_DIR)
"""Absolute path to the project root (parent of core/)."""

TEMPLATE_PATH: str = os.path.join(PROJECT_ROOT, "data", "face", "glasses.blend")
"""Path to the Blender template file containing shaders, cameras, and glasses."""

# Mesh and asset naming
OBJ_FILES: tuple[str, ...] = ("Eye Lens.OBJ", "Head.OBJ", "Lashes.OBJ", "Teeth.OBJ")
"""OBJ filenames when using a single combined eye mesh (use_common_eye_mesh=True)."""

OBJ_FILES_SEPARATE_EYES: tuple[str, ...] = ("Head.OBJ", "Lashes.OBJ", "Teeth.OBJ")
"""OBJ filenames in model obj_dir when use_common_eye_mesh=False. Eye mesh comes from EYES_DIR."""

EYES_DIR: str = os.path.join(PROJECT_ROOT, "data", "eyes")
"""Directory for the shared alternate eye mesh (use_common_eye_mesh=False). Place eye_lens.OBJ and eye_lens.mtl here."""

EYE_NEW_OBJ_FILENAME: str = "eye_lens.OBJ"
"""Filename of the alternate eye mesh in EYES_DIR; imported twice (left, right)."""

FACE_COLLECTION_NAME: str = "Face"
"""Blender collection name for all face meshes."""

EYE_BASE_NAME: str = "Eye Lens"
EYE_LEFT_NAME: str = f"{EYE_BASE_NAME} Left"
EYE_RIGHT_NAME: str = f"{EYE_BASE_NAME} Right"

# Target and eye-tracking
TARGET_OBJECT_NAME: str = "Target"
TARGET_INIT_LOCATION: tuple[float, float, float] = (0.0, -0.2, 0.3)
TARGET_SCALE: tuple[float, float, float] = (0.02, 0.02, 0.02)
TRACK_AXIS: str = "TRACK_Z"
UP_AXIS: str = "UP_Y"

# Cameras and glasses
CAMERA_LEFT_NAME: str = "Left"
CAMERA_RIGHT_NAME: str = "Right"
GLASSES_OBJECT_NAME: str = "Glasses"

# Output
RENDER_OUTPUT_LEFT: str = "view_L.png"
RENDER_OUTPUT_RIGHT: str = "view_R.png"
RENDER_CONFIG_FILENAME: str = "render_config.json"
DEFAULT_BLEND_FILENAME: str = "result.blend"
