"""
Project-wide definitions: paths, asset names, and scene object identifiers.
"""
import os

_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT: str = os.path.dirname(_CONFIG_DIR)

TEMPLATE_PATH: str = os.path.join(PROJECT_ROOT, "data", "glasses.blend")

OBJ_FILES: tuple[str, ...] = ("Eye Lens.OBJ", "Head.OBJ", "Lashes.OBJ", "Teeth.OBJ")
OBJ_FILES_SEPARATE_EYES: tuple[str, ...] = ("Head.OBJ", "Lashes.OBJ", "Teeth.OBJ")
EYES_DIR: str = os.path.join(PROJECT_ROOT, "data", "eyes")
EYE_NEW_OBJ_FILENAME: str = "eye_lens.OBJ"

FACE_COLLECTION_NAME: str = "Face"
EYE_BASE_NAME: str = "Eye Lens"
EYE_LEFT_NAME: str = f"{EYE_BASE_NAME} Left"
EYE_RIGHT_NAME: str = f"{EYE_BASE_NAME} Right"

TARGET_OBJECT_NAME: str = "Target"
TARGET_INIT_LOCATION: tuple[float, float, float] = (0.0, -0.2, 0.3)
TARGET_SCALE: tuple[float, float, float] = (0.02, 0.02, 0.02)
TRACK_AXIS: str = "TRACK_Z"
UP_AXIS: str = "UP_Y"

CAMERA_LEFT_NAME: str = "Left"
CAMERA_RIGHT_NAME: str = "Right"
GLASSES_OBJECT_NAME: str = "Glasses"

RENDER_OUTPUT_LEFT: str = "view_L.png"
RENDER_OUTPUT_RIGHT: str = "view_R.png"
RENDER_CONFIG_FILENAME: str = "render_config.json"
DEFAULT_BLEND_FILENAME: str = "result.blend"
