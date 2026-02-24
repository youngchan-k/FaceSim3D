"""
Core pipeline package for face rendering.

Structure (distinct from sample/):
  - defs:      path and name constants
  - settings: Config and save_params
  - bpy_helpers: Blender context/collection helpers
  - meshes:    OBJ validation, import, eye split
  - gaze:     target, eye tracking, cameras, glasses, skin curve
  - textures: material assignment, texture and HDRI loading
  - export:   stereo render and blend save
"""
