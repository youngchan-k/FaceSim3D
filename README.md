# Face Rendering Pipeline

A **Blender (bpy) pipeline** for generating photorealistic stereo face images. Loads `glasses.blend` as the base scene (cameras + glasses), imports a 3D face model (head, eyes, lashes, teeth), configures gaze tracking with kappa-angle correction, applies materials and HDR environment lighting, then renders a left/right stereo pair suitable for VR or 3D display applications.

## Overview

- **Input:** Base scene (`glasses.blend`), face model OBJs, textures, HDRI
- **Output:** Stereo image pair, saved Blender scene, run configuration JSON
- **Pipeline:** Import → eye tracking setup → materials → lighting → render → save

## Requirements

- Blender with `bpy` Python API
- Face models in `data/face/{gender}/{model_num}/OBJ/` and `data/face/{gender}/{model_num}/Textures/`
- Separate eye models in `data/eyes/`
- Base scene: `data/face/glasses.blend` (cameras and glasses)
- HDRIs in `data/hdri/`

## Face Model, Eye Lens & Glasses Download

Download from [Google Drive](https://drive.google.com/drive/folders/1amonkG4bumFCZ8tylnzKeQfDs6fKSZrU?usp=sharing).

**Included:**

- Face model OBJs and textures
- **Eye lens:** `Eye Lens.OBJ` (in each model’s OBJ folder; single mesh, split into left/right in-pipeline) and **`eye_lens.OBJ`** (alternate mesh for separate left/right control)
- Base scene: `glasses.blend`

**Separate eye mode:** Download **`eye_lens.OBJ`** (with **`eye_lens.mtl`**) and place them in **`data/eyes/`** (create the folder if needed). Used when `use_common_eye_mesh=False`.

## HDRI Download

Use [polydown](https://github.com/agmmnn/polydown) to download HDRIs from Poly Haven:

```bash
pip install polydown
polydown hdris -f data/hdri -s 4k -ff exr
```

## Run

```bash
blender --background --python run.py
```

(Or open Blender and run `run.py` from the Scripting workspace.)

## Outputs

| File | Description |
|------|-------------|
| `view_L.png` | Left-camera stereo view |
| `view_R.png` | Right-camera stereo view |
| `result.blend` | Saved Blender scene (textures packed) |
| `render_config.json` | Run parameters for reproducibility |

All outputs are written to the `out/` directory (configurable via `Config.save_dir`).

## Config

Configuration is in **`core/settings.py`**: the `Config` dataclass and `save_params()`. Edit defaults there or override when constructing `Config(...)` in `run.py`.

**Key options:** `gender`, `model_num`, `eye_texture_num`, `target_location`, `cam_rotation`, `hdri_name`, `render_samples`, `render_resolution_x`/`y`, `glasses_location`/`rotation`/`scale`.

### Eye mesh mode

- **`use_common_eye_mesh=True` (default)**
  Same as the sample pipeline: one **`Eye Lens.OBJ`** is imported, then split by loose parts into left and right. No per-eye position or scale.

- **`use_common_eye_mesh=False`**
  Same as project_backup: **`eye_lens.OBJ`** from **`data/eyes/`** is imported **twice** (once for left, once for right). You can set independent position and scale per eye:
  - `eye_left_location`, `eye_right_location` (x, y, z in m)
  - `eye_left_scale`, `eye_right_scale` (x, y, z)

Ensure **`data/eyes/eye_lens.OBJ`** and **`data/eyes/eye_lens.mtl`** exist (download from Google Drive and place in that folder).

## Project layout

- **`run.py`** — Entry point; runs the full pipeline.
- **`core/`** — Pipeline package: `defs`, `settings`, `bpy_helpers`, `meshes`, `gaze`, `textures`, `export`.
