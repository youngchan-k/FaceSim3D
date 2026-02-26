# Face Rendering Pipeline

A **Blender (bpy)** pipeline for **gaze-conditioned stereo face images**: load base scene, import face model, set up eye gaze (target + kappa), materials, and lighting, then render **two views from cameras in the glasses** (left and right eye).

## Overview

- **Focus:** Renders **two images** from **cameras mounted in the glasses** (left and right eye), showing a 3D face with configurable **eye gaze** — the face’s eyes look at a target with optional kappa angles. The two outputs form a stereo pair for 3D viewing or analysis.
- **Input:** Base scene (`glasses.blend`), face model OBJs, textures, HDRI
- **Output:** Stereo image pair (`view_L.png`, `view_R.png`) from the glasses’ left/right cameras, plus saved Blender scene and run configuration JSON
- **Pipeline:** Import meshes → eye tracking (gaze target + kappa) → materials & HDRI → cameras in glasses & glasses pose → render both eye views → save blend & config

## Folder structure

```
FaceSim3D/
├── data/
│   ├── glasses.blend          # Base scene (cameras in glasses, glasses object)
│   ├── face/
│   │   └── {gender}/{model_num}/
│   │       ├── OBJ/           # Head.OBJ, Eye Lens.OBJ (or Head, Lashes, Teeth for separate-eye mode)
│   │       └── Textures/
│   ├── eyes/                  # For separate eye mode only
│   │   ├── eye_lens.OBJ
│   │   └── eye_lens.mtl       # (download from Google Drive)
│   └── hdri/                  # .exr environment maps
├── config/                    # Paths, constants, Config, save_params
│   ├── defs.py
│   └── settings.py
├── bpy_utils/                 # Blender helpers (object mode, collections, origin)
│   └── helpers.py
├── mesh/                      # OBJ path check, import, eye split
│   └── meshes.py
├── scene/                     # Target, eye tracking, cameras, glasses, skin curve
│   └── gaze.py
├── materials/                 # Material assignment, textures, HDRI
│   └── textures.py
├── export/                    # Cycles stereo render, save .blend
│   └── render.py
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

Edit `config/settings.py` or pass options when creating `Config()` in `run.py`.

**Key options:** For **gaze:** `target_location`, `kappa_angle_horizontal`, `kappa_angle_vertical`. For scene: `gender`, `model_num`, `eye_texture_num`, `cam_rotation`, `hdri_name`, `render_samples`, `render_resolution_x`/`y`, `glasses_location`/`rotation`/`scale`.

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
| `view_L.png` | Left-eye camera (in glasses) view of the face (gaze-conditioned) |
| `view_R.png` | Right-eye camera (in glasses) view of the face (gaze-conditioned) |
| `result.blend` | Saved Blender scene (textures packed) |
| `render_config.json` | Run parameters for reproducibility |
