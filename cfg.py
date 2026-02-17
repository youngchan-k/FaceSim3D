"""Configuration and paths."""
import json
import os
from dataclasses import asdict, dataclass

_ROOT = os.path.dirname(os.path.abspath(__file__))

TEMPLATE = os.path.join(_ROOT, "data", "face", "glasses.blend")
OBJ_FILES = ["Eye Lens.OBJ", "Head.OBJ", "Lashes.OBJ", "Teeth.OBJ"]
FACE_COL = "Face"
EYE_BASE = "Eye Lens"
EYE_LEFT = f"{EYE_BASE} Left"
EYE_RIGHT = f"{EYE_BASE} Right"
TARGET_OBJ = "Target"
TARGET_POS = (0.0, -0.2, 0.3)
TARGET_SCALE = (0.02, 0.02, 0.02)
TRACK_AXIS = "TRACK_Z"
UP_AXIS = "UP_Y"


@dataclass
class Config:
    gender: str = "female"
    model_num: int = 1
    eye_texture_num: int = 2
    eye_ior: float = 1.4
    curve_x: float = 0.6
    curve_y: float = 0.3

    hdri_name: str = "goegap_4k"
    hdri_z_rot_deg: float = 30.0
    hdri_brightness: float = 1.0

    target_location: tuple = (1.0, -1.0, 0.0)
    cam_rotation: tuple = (120.0, 0.0, 36.0)
    cam_focal_length_mm: float = 50.0
    cam_sensor_width_mm: float = 36.0
    cam_sensor_height_mm: float = 24.0
    kappa_angle_horizontal: float = 0.0
    kappa_angle_vertical: float = 0.0

    glasses_location: tuple = (0.0, -0.13, 0.3)
    glasses_rotation: tuple = (90.0, 0.0, 0.0)
    glasses_scale: tuple = (0.0011, 0.0011, 0.0011)

    render_samples: int = 128
    render_resolution_x: int = 320
    render_resolution_y: int = 240
    render_device: str = "GPU"
    save_dir: str = os.path.join(_ROOT, "out")

    @property
    def face_dir(self) -> str:
        return os.path.join(_ROOT, "data", "face", self.gender, str(self.model_num))

    @property
    def obj_dir(self) -> str:
        return os.path.join(self.face_dir, "OBJ")

    @property
    def tex_dir(self) -> str:
        return os.path.join(self.face_dir, "Textures")

    @property
    def eye_tex_dir(self) -> str:
        return os.path.join(_ROOT, "data", "face", self.gender, str(self.eye_texture_num), "Textures")

    @property
    def hdri_path(self) -> str:
        return os.path.join(_ROOT, "data", "hdri", f"{self.hdri_name}.exr")


def save_params(cfg: Config) -> None:
    d = asdict(cfg)
    for k in ("cam_rotation", "target_location", "glasses_location", "glasses_rotation", "glasses_scale"):
        if isinstance(d.get(k), tuple):
            d[k] = list(d[k])
    os.makedirs(cfg.save_dir, exist_ok=True)
    with open(os.path.join(cfg.save_dir, "render_config.json"), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
