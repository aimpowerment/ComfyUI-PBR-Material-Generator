<div id="top"></div>

# ComfyUI PBR Material Generator

![Python](https://shields.io)
![PyTorch](https://shields.io)
![Three.js](https://shields.io)
![Offline](https://shields.io)
![License](https://shields.io)

🌐 **Language / Sprache / Langue / Idioma / Язык / 语言:**  
[<img src="https://jsdelivr.net" width="20" height="15" alt="EN"> English](#english) | [<img src="https://jsdelivr.net" width="20" height="15" alt="DE"> Deutsch](#deutsch) | [<img src="https://jsdelivr.net" width="20" height="15" alt="FR"> Français](#français) | [<img src="https://jsdelivr.net" width="20" height="15" alt="ES"> Español](#español) | [<img src="https://jsdelivr.net" width="20" height="15" alt="RU"> Русский](#русский) | [<img src="https://jsdelivr.net" width="20" height="15" alt="ZH"> 中文](#中文)

---

<a id="english"></a>
## <img src="https://jsdelivr.net" width="24" height="18" alt="EN"> English

An all-in-one **PBR Material Generator & Interactive Three.js 3D Preview Node** for ComfyUI.  
Generate **Albedo (De-Lit Base Color)**, **Depth/Height**, **Normal (Macro + Micro Detail Mix)**, **Roughness**, **Metalness**, and **Multi-Scale Ambient Occlusion** maps from a single image—or plug in your own custom PBR maps and HDR/EXR environment maps—and inspect, relight, and export the displaced mesh as **GLB** or **OBJ** directly inside ComfyUI.

### Features

- **Single-Image Full PBR Generation:** Automatically computes 6 PBR outputs from a single `IMAGE` input:
  - `base_color` with optional **Albedo De-Lighting** (`delight_strength`) to remove baked-in shadows and highlights.
  - `depth_map` with adjustable contrast, smoothness, and depth inversion.
  - `normal_map` combining macro smoothness and high-frequency micro-detail blending (`detail_mix`) plus OpenGL/DirectX Y-axis flip (`invert_normal_y`).
  - `roughness_map` with configurable base roughness (`roughness_base`), contrast, and inversion.
  - `metalness_map` via luminance and chroma thresholding.
  - `ao_map` via multi-scale cavity/horizon occlusion.
- **Custom Map Overrides:** Optionally override any generated map in the 3D viewer with custom `height_depth`, `normal_map`, `roughness_map`, `metalness_map`, `ao_map`, or `env_map` inputs.
- **10 Built-in 3D Preview Meshes:** Switch live between `Plane (Relief)`, `Box`, `Sphere`, `Cylinder`, `Cone`, `Torus`, `TorusKnot`, `Capsule`, `Dodecahedron`, and `Icosahedron` with seamless edge-faded displacement.
- **9 Kelvin Lighting Presets:** From `Candle (1900 K)` and `Gallery Warm (3200 K)` to `Daylight (5500 K)`, `Overcast (7500 K)`, and `Gallery Contrast (3000K / 7000K)`.
- **Environment Lighting & UV Tiling:** Toggle environment background visibility (`Env BG`), adjust `Env Int` and real-time `Env Blur`, and test seamless tiling (`1x` – `4x`).
- **Gallery Frame & Solo Map Inspection:** Preview with optional dark or bronze shadow-gap frames, wireframe overlay, and solo map views (`Base`, `Depth`, `Normal`, `Roughness`, `Metalness`, `AO`).
- **1-Click Baked 3D Export:** Export displaced geometry directly to binary **`.glb`**, **`.obj`**, or high-res **`.png`** preview screenshot, or copy material settings via **Copy Config**.
- **100% Offline Ready:** Bundles Three.js locally (`web/three_bundle.min.js`) with zero external CDN requests at runtime.

### Installation

1. Navigate to your ComfyUI `custom_nodes` directory:
   ```bash
   cd ComfyUI/custom_nodes
   ```
2. Clone this repository:
   ```bash
   git clone https://github.com<YOUR-USERNAME>/ComfyUI-PBR-Material-Generator.git
   ```
3. Restart ComfyUI and refresh your browser (`Ctrl + Shift + R`).

### Usage

1. Add the node via **Right-Click → Add Node → 3D/Preview → `PBR Material Generator`**.
2. Connect any `IMAGE` to the `image` input and click **Run**.
3. Use the interactive HUD (top-right) to tune displacement depth, normal strength, roughness, metalness, AO, light intensity, environment intensity, and environment blur in real time.
4. Use the bottom bar to switch 3D primitives, inspect solo maps, change Kelvin lighting temperatures, toggle UV tiling (`1x`–`4x`), or export your displaced mesh as `.glb` or `.obj`.

### License

Code in this repository is licensed under the **MIT License** (attribution required). See `THIRD-PARTY-LICENSES.txt` for bundled Three.js and fflate license notices.

[↑ Back to top](#top)
