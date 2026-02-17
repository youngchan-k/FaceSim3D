# Face Rendering Pipeline

A **Blender (bpy) pipeline** for generating photorealistic stereo face images. Loads `glasses.blend` as the base scene (cameras + glasses), imports a 3D face model (head, eyes, lashes, teeth), configures gaze tracking with kappa-angle correction, applies materials and HDR environment lighting, then renders a left/right stereo pair suitable for VR or 3D display applications.

## Overview

- **Input:** Base scene (`glasses.blend`), face model OBJs, textures, HDRI
- **Output:** Stereo image pair, saved Blender scene, run configuration JSON
- **Pipeline:** Import → eye tracking setup → materials → lighting → render → save

## Requirements

- Blender with `bpy` Python API
- Face models in `data/face/{gender}/{model_num}/OBJ/` and `data/face/{gender}/{model_num}/Textures/`
- Base scene: `data/face/glasses.blend` (cameras and glasses)
- HDRIs in `data/hdri/`

## Data structure

```
data/
├── face/
│   ├── glasses.blend          # Base scene
│   ├── female/
│   │   ├── 1/                 # model_num
│   │   │   ├── OBJ/           # Eye Lens.OBJ, Head.OBJ, Lashes.OBJ, Teeth.OBJ
│   │   │   └── Textures/      # Colour_8k.jpg, Gloss.jpg, Spec.jpg, Eye Colour.jpg, Teeth.jpg
│   │   └── 2/
│   └── male/
│       ├── 1/
│       └── 2/
└── hdri/                      # goegap_4k.exr, etc.
```

## Face Model & Glasses Download

Download from [Google Drive](https://drive.google.com/drive/folders/1amonkG4bumFCZ8tylnzKeQfDs6fKSZrU?usp=sharing).

**Included:** Face model OBJs and textures, `glasses.blend` (base scene).

## HDRI Download

Use [polydown](https://github.com/agmmnn/polydown) to download HDRIs from Poly Haven:

```bash
cd project_1
pip install polydown
polydown hdris -f data/hdri -s 4k -ff exr
```

## Run

```bash
cd project_1 && blender --background --python run.py
```

## Outputs

| File | Description |
|------|-------------|
| `view_L.png` | Left-camera stereo view |
| `view_R.png` | Right-camera stereo view |
| `result.blend` | Saved Blender scene (textures packed) |
| `render_config.json` | Run parameters for reproducibility |

All outputs are written to the `out/` directory.

## Config

Edit defaults in `cfg.py` or override when constructing `Config(...)` in `run.py`. Key options: `gender`, `model_num`, `eye_texture_num`, `target_location`, `cam_rotation`, `hdri_name`, `render_samples`, `render_resolution_x`/`y`, `glasses_location`/`rotation`/`scale`.
