"""
Pipeline settings: Config dataclass and JSON persistence.
"""
import json
import os
from dataclasses import asdict, dataclass

from config.defs import PROJECT_ROOT, RENDER_CONFIG_FILENAME


@dataclass
class Config:
    """
    Runtime configuration for the face rendering pipeline.
    Paths are derived from PROJECT_ROOT. Units: meters for locations, degrees for angles.
    """
    gender: str = "female"
    model_num: int = 1
    eye_texture_num: int = 2
    eye_ior: float = 1.4
    use_common_eye_mesh: bool = True
    eye_left_location: tuple[float, float, float] = (0.0, 0.0, 0.0)
    eye_right_location: tuple[float, float, float] = (0.0, 0.0, 0.0)
    eye_left_scale: tuple[float, float, float] = (1.0, 1.0, 1.0)
    eye_right_scale: tuple[float, float, float] = (1.0, 1.0, 1.0)
    curve_x: float = 0.6
    curve_y: float = 0.3
    hdri_name: str = "goegap_4k"
    hdri_z_rot_deg: float = 30.0
    hdri_brightness: float = 1.0
    target_location: tuple[float, float, float] = (1.0, -1.0, 0.0)
    cam_rotation: tuple[float, float, float] = (120.0, 0.0, 36.0)
    cam_focal_length_mm: float = 50.0
    cam_sensor_width_mm: float = 36.0
    cam_sensor_height_mm: float = 24.0
    kappa_angle_horizontal: float = 0.0
    kappa_angle_vertical: float = 0.0
    glasses_location: tuple[float, float, float] = (0.0, -0.13, 0.3)
    glasses_rotation: tuple[float, float, float] = (90.0, 0.0, 0.0)
    glasses_scale: tuple[float, float, float] = (0.0011, 0.0011, 0.0011)
    render_samples: int = 128
    render_resolution_x: int = 320
    render_resolution_y: int = 240
    render_device: str = "GPU"
    save_dir: str = os.path.join(PROJECT_ROOT, "out")

    @property
    def face_dir(self) -> str:
        return os.path.join(PROJECT_ROOT, "data", "face", self.gender, str(self.model_num))

    @property
    def obj_dir(self) -> str:
        return os.path.join(self.face_dir, "OBJ")

    @property
    def tex_dir(self) -> str:
        return os.path.join(self.face_dir, "Textures")

    @property
    def eye_tex_dir(self) -> str:
        return os.path.join(
            PROJECT_ROOT, "data", "face", self.gender, str(self.eye_texture_num), "Textures"
        )

    @property
    def hdri_path(self) -> str:
        return os.path.join(PROJECT_ROOT, "data", "hdri", f"{self.hdri_name}.exr")


def save_params(cfg: Config, filename: str | None = None) -> None:
    """Write config to JSON in cfg.save_dir. Tuples serialized as lists."""
    filename = filename or RENDER_CONFIG_FILENAME
    data = asdict(cfg)
    tuple_keys = (
        "cam_rotation", "target_location", "glasses_location", "glasses_rotation", "glasses_scale",
        "eye_left_location", "eye_right_location", "eye_left_scale", "eye_right_scale",
    )
    for k in tuple_keys:
        if isinstance(data.get(k), tuple):
            data[k] = list(data[k])
    os.makedirs(cfg.save_dir, exist_ok=True)
    with open(os.path.join(cfg.save_dir, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
