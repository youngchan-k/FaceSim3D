"""
Pipeline settings: Config dataclass and JSON persistence.

Distinct from sample/utils/config.py. Provides Config and save_params.
"""
import json
import os
from dataclasses import asdict, dataclass

from core.defs import PROJECT_ROOT, RENDER_CONFIG_FILENAME


@dataclass
class Config:
    """
    Runtime configuration for the face rendering pipeline.

    All paths (face_dir, obj_dir, tex_dir, eye_tex_dir, hdri_path, save_dir) are
    derived from PROJECT_ROOT and the fields below. Units are meters for
    locations and degrees for angles unless noted otherwise.

    --- Face model ---
    gender: Gender of the face model. Used to select the subfolder under
        data/face/<gender>/<model_num>/ and data/face/<gender>/<eye_texture_num>/.
    model_num: Model identifier (integer). Determines which head/eyes/lashes/teeth
        OBJ and textures are loaded.
    eye_texture_num: Separate identifier for eye texture set. Allows using
        a different eye appearance than the model number.
    eye_ior: Index of refraction for the eye Principled BSDF. Typical human
        value is around 1.4.

    --- Eye mesh mode ---
    use_common_eye_mesh: If True, use "Eye Lens.OBJ" and split into left/right (default).
        If False, import "eye_lens.OBJ" from data/eyes/ twice (once for left, once for right)
        with independent size and position per eye (eye_*_location, eye_*_scale).
    eye_left_location: World position (x, y, z) for the left eye when
        use_common_eye_mesh=False. Units: m.
    eye_right_location: World position (x, y, z) for the right eye when
        use_common_eye_mesh=False. Units: m.
    eye_left_scale: Scale (x, y, z) for the left eye when use_common_eye_mesh=False.
    eye_right_scale: Scale (x, y, z) for the right eye when use_common_eye_mesh=False.

    --- Skin tone (RGB curve) ---
    curve_x: X coordinate (0–1) of the control point on the head's RGB Curves node.
    curve_y: Y coordinate (0–1) of that control point. Together with curve_x
        used for color grading / skin tone adjustment.

    --- HDRI environment ---
    hdri_name: Base name of the HDRI file (e.g. "goegap_4k") under data/hdri/.
        File is expected as <hdri_name>.exr.
    hdri_z_rot_deg: Rotation in degrees around Z for the environment mapping.
    hdri_brightness: Multiplier for the world Background node strength.

    --- Gaze target and camera ---
    target_location: World position (x, y, z) where the face looks. Convention:
        +x left, -y forward, +z up.
    cam_rotation: Euler rotation (deg) applied to both Left and Right cameras.
    cam_focal_length_mm: Camera lens focal length in mm.
    cam_sensor_width_mm: Camera sensor width in mm.
    cam_sensor_height_mm: Camera sensor height in mm.
    kappa_angle_horizontal: Horizontal kappa (deg): angular offset between
        visual and pupillary axis. Positive = nasal.
    kappa_angle_vertical: Vertical kappa (deg). Positive = upward.

    --- Glasses object ---
    glasses_location: World position (x, y, z) of the Glasses object.
    glasses_rotation: Rotation (x, y, z) in degrees.
    glasses_scale: Scale (x, y, z). Use small values (e.g. 0.0011) for
        real-world scale glasses in meter-based scenes.

    --- Render and output ---
    render_samples: Cycles samples per pixel.
    render_resolution_x: Output image width in pixels.
    render_resolution_y: Output image height in pixels.
    render_device: "CPU" or "GPU".
    save_dir: Directory where renders, result.blend, and render_config.json
        are written.
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
