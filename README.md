# Face Rendering Pipeline

A **Blender (bpy)** pipeline for stereo face images: load base scene, import face model, set up gaze and materials, render left/right pair.

## Overview

- **Input:** Base scene (`glasses.blend`), face model OBJs, textures, HDRI
- **Output:** Stereo image pair, saved Blender scene, run configuration JSON
- **Pipeline:** Import → eye tracking setup → materials → lighting → render → save

## Folder structure


```
FaceSim3D/
├── data/
│   ├── glasses.blend          # Base scene (cameras, glasses)
│   ├── face/
│   │   └── {gender}/{model_num}/
│   │       ├── OBJ/           # Head.OBJ, Eye Lens.OBJ (or Head, Lashes, Teeth for separate-eye mode)
│   │       └── Textures/
│   ├── eyes/                  # For separate eye mode only
│   │   ├── eye_lens.OBJ
│   │   └── eye_lens.mtl       # (download from Google Drive)
│   └── hdri/                  # .exr environment maps
├── core/                      # Pipeline package
│   ├── defs.py                # Paths, asset names, scene constants
│   ├── settings.py            # Config dataclass, save_params()
│   ├── bpy_helpers.py         # Blender helpers (object mode, collections, origin)
│   ├── meshes.py              # OBJ path check, import, eye split (common/separate)
│   ├── gaze.py                # Target, eye tracking, cameras, glasses, skin curve
│   ├── textures.py            # Material assignment, head/eye/teeth textures, HDRI
│   └── export.py              # Cycles stereo render, save .blend
├── run.py                     # Entry point
└── out/                       # Renders, result.blend, render_config.json (default)
```

## Downloading assets

**3D assets** — Download from [Google Drive](https://drive.google.com/drive/folders/1amonkG4bumFCZ8tylnzKeQfDs6fKSZrU?usp=sharing) and place files as in the folder structure above.

**HDRIs** — Use [polydown](https://github.com/agmmnn/polydown) to download HDRIs from Poly Haven:

```bash
pip install polydown
polydown hdris -f data/hdri -s 4k -ff exr
```

## Configuration

Edit `core/settings.py` or pass options when creating `Config()` in `run.py`.

**Key options:** `gender`, `model_num`, `eye_texture_num`, `target_location`, `cam_rotation`, `hdri_name`, `render_samples`, `render_resolution_x`/`y`, `glasses_location`/`rotation`/`scale`.

**Mode setting:**
| Mode | `use_common_eye_mesh` | Eye mesh | Behavior |
|------|------------------------|----------|----------|
| **Common** | `True` | `Eye Lens.OBJ` (in each model’s OBJ folder) | One mesh imported, split by loose parts into left/right. No per-eye position or scale. |
| **Separate** | `False` | `eye_lens.OBJ` in `data/eyes/` | Same mesh imported twice (left, right). Independent position and scale per eye. |

## Run

Requires **Blender** (with **`bpy`**). No extra packages.

```bash
blender --background --python run.py
```

## Outputs

All outputs are written to the `out/` directory (configurable via `Config.save_dir`).

| File | Description |
|------|-------------|
| `view_L.png` | Left-camera stereo view |
| `view_R.png` | Right-camera stereo view |
| `result.blend` | Saved Blender scene (textures packed) |
| `render_config.json` | Run parameters for reproducibility |
