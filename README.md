<div id="top"></div>

# ComfyUI PBR Material Generator

🌐 **Language / Sprache / Langue / Idioma / Язык / 语言:**  
[<img src="https://githubusercontent.com" width="20" height="15" alt="EN"> English](#english) | [<img src="https://githubusercontent.com" width="20" height="15" alt="DE"> Deutsch](#deutsch) | [<img src="https://githubusercontent.com" width="20" height="15" alt="FR"> Français](#français) | [<img src="https://githubusercontent.com" width="20" height="15" alt="ES"> Español](#español) | [<img src="https://githubusercontent.com" width="20" height="15" alt="RU"> Русский](#русский) | [<img src="https://githubusercontent.com" width="20" height="15" alt="ZH"> 中文](#中文)

---

<a id="english"></a>
## <img src="https://githubusercontent.com" width="24" height="18" alt="EN"> English

An all-in-one **PBR Material Generator & Interactive Three.js 3D Preview Node** for ComfyUI to generate, inspect, and export full PBR maps and displaced 3D meshes (GLB/OBJ) from a single image.

### Features
- **Full PBR Generation:** Computes Albedo (with optional de-lighting), Depth, Normal, Roughness, Metalness, and AO maps from a single `IMAGE` input.
- **Custom Map Overrides & 3D Tools:** Supports custom map inputs, 10 built-in 3D preview meshes, 9 Kelvin lighting presets, environment controls, and solo map inspection.
- **Export & Offline Support:** 1-click export to `.glb`, `.obj`, or high-res `.png` screenshots, running 100% offline via a bundled local Three.js build.

### Installation & Usage
1. Clone the repository into your ComfyUI `custom_nodes` folder:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com
   ```
2. Restart ComfyUI, add the `PBR Material Generator` node via right-click, connect an `IMAGE`, and use the interactive HUD or export options.

### License
Licensed under the **MIT License**. See repository files for bundled third-party notices.

[↑ Back to top](#top)
