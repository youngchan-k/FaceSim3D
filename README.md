# Face Rendering Pipeline

A **Blender (bpy) pipeline** for generating photorealistic stereo face images. Loads `glasses.blend` as the base scene (cameras + glasses), imports a 3D face model (head, eyes, lashes, teeth), configures gaze tracking with kappa-angle correction, applies materials and HDR environment lighting, then renders a left/right stereo pair suitable for VR or 3D display applications.

## Overview

- **Input:** Base scene (`glasses.blend`), face model OBJs, textures, HDRI
- **Output:** Stereo image pair, saved Blender scene, run configuration JSON
- **Pipeline:** Import → eye tracking setup → materials → lighting → render → save

## Requirements

- Blender with `bpy` Python API
- Face models in `data/face/{gender}/{model_num}/OBJ/` and `data/face/{gender}/{model_num}/Textures/`
- Separate eye models in `data/eyes/` (for separate eye mode)
- Base scene: `data/glasses.blend` (cameras and glasses)
- HDRIs in `data/hdri/`

## Folder structure

Expected layout under the project root (create folders as needed):

```
data/
├── glasses.blend              # Base scene (cameras, glasses)
├── face/
│   └── {gender}/{model_num}/
│       ├── OBJ/               # Head.OBJ, Eye Lens.OBJ (or Head, Lashes, Teeth for separate-eye mode), etc.
│       └── Textures/
├── eyes/                      # For separate eye mode only
│   ├── eye_lens.OBJ
│   └── eye_lens.mtl           # (download from Google Drive)
└── hdri/                      # .exr environment maps
run.py                         # Entry point
core/                          # Pipeline package
out/                           # Renders, result.blend, render_config.json (default)
```

## Downloading assets

**3D assets (face models, eye lens, base scene)**
Download from [Google Drive](https://drive.google.com/drive/folders/1amonkG4bumFCZ8tylnzKeQfDs6fKSZrU?usp=sharing). Place face model OBJs and textures in `data/face/{gender}/{model_num}/`, `glasses.blend` in `data/`, and for separate eye mode place `eye_lens.OBJ` and `eye_lens.mtl` in `data/eyes/`.

**HDRIs**
Use [polydown](https://github.com/agmmnn/polydown) to download HDRIs from Poly Haven:

```bash
pip install polydown
polydown hdris -f data/hdri -s 4k -ff exr
```

## Configuration

Edit `core/settings.py` (the `Config` dataclass) or override when constructing `Config(...)` in `run.py`.

**Key options:** `gender`, `model_num`, `eye_texture_num`, `target_location`, `cam_rotation`, `hdri_name`, `render_samples`, `render_resolution_x`/`y`, `glasses_location`/`rotation`/`scale`.

### Eye mesh mode

| Mode | `use_common_eye_mesh` | Eye mesh | Behavior |
|------|------------------------|----------|----------|
| **Common** | `True` | `Eye Lens.OBJ` (in each model’s OBJ folder) | One mesh imported, split by loose parts into left/right. No per-eye position or scale. |
| **Separate** | `False` | `eye_lens.OBJ` in `data/eyes/` | Same mesh imported twice (left, right). Independent position and scale per eye. |


## Run

```bash
blender --background --python run.py
```


## Outputs

| File | Description |
|------|-------------|
| `view_L.png` | Left-camera stereo view |
| `view_R.png` | Right-camera stereo view |
| `result.blend` | Saved Blender scene (textures packed) |
| `render_config.json` | Run parameters for reproducibility |

All outputs are written to the `out/` directory (configurable via `Config.save_dir`).