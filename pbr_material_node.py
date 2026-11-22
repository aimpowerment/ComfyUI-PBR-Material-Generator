import os
import torch
import torch.nn.functional as F
import folder_paths
from PIL import Image
import numpy as np

_base_dir = os.path.dirname(os.path.abspath(__file__))
_web_dir = os.path.join(_base_dir, "web")
os.makedirs(_web_dir, exist_ok=True)

EXT_JS = [
    'import { app } from "../../scripts/app.js";',
    'app.registerExtension({',
    '  name: "Comfy.FullPBRThreeJSPreview",',
    '  async beforeRegisterNodeDef(nodeType, nodeData) {',
    '    if (nodeData.name !== "FullPBRThreeJSPreview") return;',
    '    const onNodeCreated = nodeType.prototype.onNodeCreated;',
    '    nodeType.prototype.onNodeCreated = function () {',
    '      if (onNodeCreated) onNodeCreated.apply(this, arguments);',
    '      const node = this;',
    '      const container = document.createElement("div");',
    '      container.style.cssText = "width:100%;height:100%;min-height:260px;background:#141417;border-radius:6px;overflow:hidden;position:relative;box-sizing:border-box;";',
    '      const iframe = document.createElement("iframe");',
    '      iframe.style.cssText = "position:absolute;inset:0;width:100%;height:100%;border:none;display:block;";',
    '      container.appendChild(iframe);',
    '      const widget = this.addDOMWidget("threejs_pbr_viewer", "preview", container, {',
    '        getMinHeight: () => 260,',
    '        hideOnZoom: false,',
    '      });',
    '      widget.computeSize = (width) => Array.of(width, 380);',
    '      const onDrawForeground = this.onDrawForeground;',
    '      this.onDrawForeground = function (ctx) {',
    '        if (onDrawForeground) onDrawForeground.apply(this, arguments);',
    '        if (widget.last_y !== undefined && node.size) {',
    '          const availH = Math.max(260, node.size.at(1) - widget.last_y - 12);',
    '          if (container.style.height !== availH + "px") container.style.height = availH + "px";',
    '        }',
    '      };',
    '      this.setSize(Array.of(640, 880));',
    '      this.previewIframe = iframe;',
    '    };',
    '    const onExecuted = nodeType.prototype.onExecuted;',
    '    nodeType.prototype.onExecuted = function (message) {',
    '      if (onExecuted) onExecuted.apply(this, arguments);',
    '      const f = message?.pbr_files?.at(0);',
    '      if (!f || !this.previewIframe) return;',
    '      const params = new URLSearchParams({ v: "23", t: Date.now(), ...f });',
    '      this.previewIframe.src = "/extensions/ComfyUI_PBR_Preview/viewer.html?" + params.toString();',
    '    };',
    '  }',
    '});',
]

with open(os.path.join(_web_dir, "pbr_preview.js"), "w", encoding="utf-8") as f:
    f.write("\n".join(EXT_JS))

VIEWER_HTML = [
    '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>',
    'html,body{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#141417;font-family:system-ui,sans-serif;color:#eee;}',
    '#hud{position:fixed;top:8px;right:8px;z-index:10;background:rgba(20,20,23,0.88);padding:8px 10px;border-radius:6px;font-size:11px;border:1px solid rgba(255,255,255,0.12);display:flex;flex-direction:column;gap:5px;}',
    '#hud label{display:flex;justify-content:space-between;align-items:center;gap:8px;} #hud input[type=range]{width:70px;}',
    '#bar{position:fixed;bottom:8px;left:8px;right:8px;z-index:10;background:rgba(20,20,23,0.9);padding:6px 8px;border-radius:6px;font-size:11px;border:1px solid rgba(255,255,255,0.12);display:flex;flex-wrap:wrap;align-items:center;gap:6px;}',
    'select,button{background:#26262c;color:#eee;border:1px solid rgba(255,255,255,0.2);border-radius:4px;padding:3px 6px;font-size:11px;cursor:pointer;}',
    'button:hover,select:hover{background:#35353e;}',
    '</style></head><body>',
    '<div id="hud">',
    '<label>Tiefe <input id="s-depth" type="range" min="0" max="0.5" step="0.01" value="0.25"></label>',
    '<label>Normal <input id="s-norm" type="range" min="0" max="2" step="0.05" value="1.0"></label>',
    '<label>Rough <input id="s-rough" type="range" min="0" max="2" step="0.05" value="1.0"></label>',
    '<label>Metal <input id="s-metal" type="range" min="0" max="1" step="0.02" value="0.5"></label>',
    '<label>AO <input id="s-ao" type="range" min="0" max="2" step="0.05" value="1.0"></label>',
    '<label>Licht <input id="s-light" type="range" min="0" max="60" step="1" value="30"></label>',
    '<label>Env Int <input id="s-env" type="range" min="0" max="2" step="0.05" value="1.0"></label>',
    '<label>Env Blur <input id="s-blur" type="range" min="0" max="1" step="0.02" value="0.2"></label>',
    '<label>Schwenk <input id="c-auto" type="checkbox" checked></label></div>',
    '<div id="bar">',
    '<select id="sel-shape"><option value="plane">Mesh: Plane (Relief)</option><option value="box">Mesh: Box</option><option value="sphere">Mesh: Sphere</option><option value="cylinder">Mesh: Cylinder</option><option value="cone">Mesh: Cone</option><option value="torus">Mesh: Torus</option><option value="torusknot">Mesh: TorusKnot</option><option value="capsule">Mesh: Capsule</option><option value="dodecahedron">Mesh: Dodecahedron</option><option value="icosahedron">Mesh: Icosahedron</option></select>',
    '<select id="sel-view"><option value="pbr">View: Final PBR</option><option value="base">Solo: Base</option><option value="depth">Solo: Depth</option><option value="normal">Solo: Normal</option><option value="roughness">Solo: Roughness</option><option value="metalness">Solo: Metalness</option><option value="ao">Solo: AO</option></select>',
    '<select id="sel-light"><option value="candle">Licht: Kerze (1900 K)</option><option value="bulb">Licht: Glühlampe (2700 K)</option><option value="warm" selected>Licht: Galerie Warm (3200 K)</option><option value="studio">Licht: Studio (4200 K)</option><option value="daylight">Licht: Tageslicht (5500 K)</option><option value="cool">Licht: Atelier Kühl (6500 K)</option><option value="overcast">Licht: Bedeckt (7500 K)</option><option value="shade">Licht: Schatten (9500 K)</option><option value="contrast">Licht: Galerie Kontrast (3000K/7000K)</option></select>',
    '<select id="sel-frame"><option value="none">Frame: Ohne</option><option value="dark">Frame: Dunkel</option><option value="bronze">Frame: Bronze</option></select>',
    '<select id="sel-tile"><option value="1" selected>Tile: 1x</option><option value="2">Tile: 2x</option><option value="3">Tile: 3x</option><option value="4">Tile: 4x</option></select>',
    '<select id="sel-qual"><option value="128">Qual: Low</option><option value="256" selected>Qual: Bal</option><option value="384">Qual: High</option></select>',
    '<label style="display:flex;align-items:center;gap:3px;cursor:pointer;"><input id="c-wire" type="checkbox">Wire</label>',
    '<button id="btn-bg">Env BG</button>',
    '<button id="btn-reset">Reset</button>',
    '<button id="btn-cfg">Copy Config</button>',
    '<button id="btn-png">PNG</button>',
    '<span style="margin-left:auto;display:flex;align-items:center;gap:4px;"><select id="sel-fmt"><option value="glb">GLB</option><option value="obj">OBJ</option></select><button id="btn-exp">Export</button></span>',
    '</div>',
    '<script type="module">',
    'import * as THREE from "./three_bundle.min.js";',
    'const { OrbitControls, GLTFExporter, OBJExporter } = THREE;',
    'const q = new URLSearchParams(window.location.search);',
    'const ts = q.get("t") || Date.now();',
    'const getUrl = (k) => (q.get(k) ? "/view?filename=" + encodeURIComponent(q.get(k)) + "&type=temp&t=" + ts : "");',
    'const urls = { base:getUrl("base"), depth:getUrl("depth"), normal:getUrl("normal"), roughness:getUrl("roughness"), metalness:getUrl("metalness"), ao:getUrl("ao"), env:getUrl("env") };',
    'const scene = new THREE.Scene(); const bgColor = new THREE.Color(0x141417); scene.background = bgColor; scene.backgroundBlurriness = 0.2;',
    'const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 500); camera.position.set(0,0,7.8);',
    'const renderer = new THREE.WebGLRenderer({antialias:true, preserveDrawingBuffer:true}); renderer.setSize(window.innerWidth, window.innerHeight); renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.15; document.body.appendChild(renderer.domElement);',
    'const pmrem = new THREE.PMREMGenerator(renderer); pmrem.compileEquirectangularShader();',
    'let currentEnvTex = null; let showEnvBg = true; let uvTile = 1;',
    'const controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping = true;',
    'const artGroup = new THREE.Group(); scene.add(artGroup);',
    'let aspect = 1.0; let segs = 256; let shapeType = "plane";',
    'const loader = new THREE.TextureLoader(); const texStore = {};',
    'function loadPbrTex(url, isColor=false, onDone=null){ if(!url) return null; return loader.load(url, (t)=>{ if(isColor) t.colorSpace=THREE.SRGBColorSpace; t.wrapS=THREE.RepeatWrapping; t.wrapT=THREE.RepeatWrapping; t.repeat.set(uvTile, uvTile); t.needsUpdate=true; if(onDone) onDone(t); }); }',
    'texStore.base = loadPbrTex(urls.base, true, (t)=>{ aspect=t.image.width/t.image.height; rebuildGeo(); });',
    'texStore.depth = loadPbrTex(urls.depth);',
    'texStore.normal = loadPbrTex(urls.normal);',
    'texStore.roughness = loadPbrTex(urls.roughness);',
    'texStore.metalness = loadPbrTex(urls.metalness);',
    'texStore.ao = loadPbrTex(urls.ao);',
    'const pbrMat = new THREE.MeshStandardMaterial({ map:texStore.base||null, displacementMap:texStore.depth||null, displacementScale:0.25, displacementBias:0.0, normalMap:texStore.normal||null, normalScale:new THREE.Vector2(1.0,1.0), roughnessMap:texStore.roughness||null, roughness:1.0, metalnessMap:texStore.metalness||null, metalness:0.5, aoMap:texStore.ao||null, aoMapIntensity:1.0, envMapIntensity:1.0 });',
    'pbrMat.onBeforeCompile = (s) => {',
    '  s.vertexShader = s.vertexShader.replace("#include <displacementmap_vertex>", "#ifdef USE_DISPLACEMENTMAP\\nvec2 ed=min(vDisplacementMapUv,1.0-vDisplacementMapUv);float em=smoothstep(0.0,0.04,min(ed.x,ed.y));transformed+=normalize(objectNormal)*((texture2D(displacementMap,vDisplacementMapUv).x*displacementScale+displacementBias)*em);\\n#endif");',
    '};',
    'const soloMat = new THREE.MeshBasicMaterial({ color:0xffffff });',
    'const mesh = new THREE.Mesh(new THREE.PlaneGeometry(5,5,256,256), pbrMat); artGroup.add(mesh);',
    'const frameGroup = new THREE.Group(); frameGroup.visible = false; artGroup.add(frameGroup);',
    'const frameMat = new THREE.MeshStandardMaterial({color:0x1b1918, roughness:0.4, metalness:0.5});',
    'const backMat = new THREE.MeshStandardMaterial({color:0x0a0a0c, roughness:0.9});',
    'const backMesh = new THREE.Mesh(new THREE.BoxGeometry(1,1,0.08), backMat); backMesh.position.z=-0.22;',
    'const topB = new THREE.Mesh(new THREE.BoxGeometry(1,1,1), frameMat); const botB = new THREE.Mesh(new THREE.BoxGeometry(1,1,1), frameMat);',
    'const leftB = new THREE.Mesh(new THREE.BoxGeometry(1,1,1), frameMat); const rightB = new THREE.Mesh(new THREE.BoxGeometry(1,1,1), frameMat);',
    'frameGroup.add(backMesh, topB, botB, leftB, rightB);',
    'function createShapeGeo(type, w, h, s){',
    '  const sub = Math.min(s, 128);',
    '  if(type==="box") return new THREE.BoxGeometry(3.2, 3.2, 3.2, 48, 48, 48);',
    '  if(type==="sphere") return new THREE.SphereGeometry(2.1, sub, Math.floor(sub/2));',
    '  if(type==="cylinder") return new THREE.CylinderGeometry(1.6, 1.6, 3.6, sub, 48);',
    '  if(type==="cone") return new THREE.ConeGeometry(1.9, 3.8, sub, 48);',
    '  if(type==="torus") return new THREE.TorusGeometry(1.65, 0.65, Math.floor(sub/2), sub);',
    '  if(type==="torusknot") return new THREE.TorusKnotGeometry(1.4, 0.45, sub*2, Math.floor(sub/3));',
    '  if(type==="capsule") return new THREE.CapsuleGeometry(1.3, 1.8, Math.floor(sub/4), sub);',
    '  if(type==="dodecahedron") return new THREE.DodecahedronGeometry(2.1, 2);',
    '  if(type==="icosahedron") return new THREE.IcosahedronGeometry(2.1, 3);',
    '  return new THREE.PlaneGeometry(w, h, s, s);',
    '}',
    'function rebuildGeo(){ const w=5*aspect, h=5; mesh.geometry.dispose(); mesh.geometry=createShapeGeo(shapeType, w, h, segs); mesh.geometry.setAttribute("uv2",mesh.geometry.attributes.uv);',
    '  const fMode = document.getElementById("sel-frame").value;',
    '  frameGroup.visible = (shapeType==="plane" && fMode!=="none");',
    '  const gap=0.08, th=0.14, dp=0.44, iw=w+gap*2, ih=h+gap*2, ow=iw+th*2, oh=ih+th*2;',
    '  backMesh.geometry.dispose(); backMesh.geometry=new THREE.BoxGeometry(ow-0.02,oh-0.02,0.08);',
    '  topB.geometry.dispose(); topB.geometry=new THREE.BoxGeometry(ow,th,dp); topB.position.set(0,(ih+th)/2,-0.04);',
    '  botB.geometry.dispose(); botB.geometry=new THREE.BoxGeometry(ow,th,dp); botB.position.set(0,-(ih+th)/2,-0.04);',
    '  leftB.geometry.dispose(); leftB.geometry=new THREE.BoxGeometry(th,ih,dp); leftB.position.set(-(iw+th)/2,0,-0.04);',
    '  rightB.geometry.dispose(); rightB.geometry=new THREE.BoxGeometry(th,ih,dp); rightB.position.set((iw+th)/2,0,-0.04); }',
    'rebuildGeo();',
    'const amb = new THREE.AmbientLight(0xffffff, 0.55); scene.add(amb);',
    'const spot = new THREE.PointLight(0xffebd2, 30, 25); spot.position.set(2.5,2.5,3.2); scene.add(spot);',
    'const fill = new THREE.DirectionalLight(0xdbeafe, 0.6); fill.position.set(-4,-3,2); scene.add(fill);',
    'if(urls.env){',
    '  loader.load(urls.env, (tex) => {',
    '    tex.mapping = THREE.EquirectangularReflectionMapping;',
    '    tex.colorSpace = THREE.SRGBColorSpace;',
    '    const envRT = pmrem.fromEquirectangular(tex).texture;',
    '    currentEnvTex = envRT;',
    '    scene.environment = envRT;',
    '    pbrMat.envMap = envRT;',
    '    pbrMat.needsUpdate = true;',
    '    frameMat.envMap = envRT;',
    '    frameMat.needsUpdate = true;',
    '    if(showEnvBg) scene.background = envRT;',
    '    tex.dispose();',
    '  });',
    '}',
    'const lightPresets = {',
    '  candle:   { main: 0xff9329, fill: 0xffb86c, amb: 0.35 },',
    '  bulb:     { main: 0xffc58f, fill: 0xffe4c4, amb: 0.45 },',
    '  warm:     { main: 0xffebd2, fill: 0xdbeafe, amb: 0.55 },',
    '  studio:   { main: 0xfff5e8, fill: 0xf1f5f9, amb: 0.60 },',
    '  daylight: { main: 0xffffff, fill: 0xf8fafc, amb: 0.65 },',
    '  cool:     { main: 0xe6f0ff, fill: 0xcbd5e1, amb: 0.60 },',
    '  overcast: { main: 0xd4e4ff, fill: 0x94a3b8, amb: 0.70 },',
    '  shade:    { main: 0xbcd4ff, fill: 0x64748b, amb: 0.55 },',
    '  contrast: { main: 0xffd9b3, fill: 0x93c5fd, amb: 0.45 }',
    '};',
    'document.getElementById("sel-shape").onchange=(e)=>{ shapeType=e.target.value; rebuildGeo(); };',
    'document.getElementById("sel-tile").onchange=(e)=>{ uvTile=parseInt(e.target.value); Object.values(texStore).forEach((t)=>{ if(t){ t.repeat.set(uvTile, uvTile); t.needsUpdate=true; } }); };',
    'document.getElementById("s-depth").oninput=(e)=>pbrMat.displacementScale=parseFloat(e.target.value);',
    'document.getElementById("s-norm").oninput=(e)=>{const v=parseFloat(e.target.value);pbrMat.normalScale.set(v,v);};',
    'document.getElementById("s-rough").oninput=(e)=>pbrMat.roughness=parseFloat(e.target.value);',
    'document.getElementById("s-metal").oninput=(e)=>pbrMat.metalness=parseFloat(e.target.value);',
    'document.getElementById("s-ao").oninput=(e)=>pbrMat.aoMapIntensity=parseFloat(e.target.value);',
    'document.getElementById("s-light").oninput=(e)=>spot.intensity=parseFloat(e.target.value);',
    'document.getElementById("s-env").oninput=(e)=>{ pbrMat.envMapIntensity=parseFloat(e.target.value); frameMat.envMapIntensity=parseFloat(e.target.value); };',
    'document.getElementById("s-blur").oninput=(e)=>{ scene.backgroundBlurriness=parseFloat(e.target.value); };',
    'let auto=true; document.getElementById("c-auto").onchange=(e)=>auto=e.target.checked;',
    'document.getElementById("sel-view").onchange=(e)=>{ const v=e.target.value; if(v==="pbr"){ mesh.material=pbrMat; } else { soloMat.map=texStore[v]||null; soloMat.needsUpdate=true; mesh.material=soloMat; } };',
    'document.getElementById("sel-light").onchange=(e)=>{ const p=lightPresets[e.target.value]; if(p){ spot.color.set(p.main); fill.color.set(p.fill); amb.intensity=p.amb; } };',
    'document.getElementById("sel-frame").onchange=(e)=>{ const v=e.target.value; frameGroup.visible=(shapeType==="plane" && v!=="none"); if(v==="dark"){frameMat.color.set(0x1b1918);frameMat.metalness=0.4;} if(v==="bronze"){frameMat.color.set(0x4a3928);frameMat.metalness=0.75;} };',
    'document.getElementById("sel-qual").onchange=(e)=>{ segs=parseInt(e.target.value); rebuildGeo(); };',
    'document.getElementById("c-wire").onchange=(e)=>{ pbrMat.wireframe=e.target.checked; soloMat.wireframe=e.target.checked; };',
    'document.getElementById("btn-reset").onclick=()=>{ camera.position.set(0,0,7.8); controls.target.set(0,0,0); controls.update(); };',
    'document.getElementById("btn-bg").onclick=()=>{ showEnvBg=!showEnvBg; scene.background=(showEnvBg && currentEnvTex)?currentEnvTex:bgColor; };',
    'document.getElementById("btn-cfg").onclick=(e)=>{ const lTxt=document.getElementById("sel-light").selectedOptions.at(0)?.text||""; const cfg=`mesh: ${shapeType},\\nuvTiling: ${uvTile}x,\\nlichtProfil: "${lTxt}",\\ntiefe: ${pbrMat.displacementScale},\\nnormalStaerke: ${pbrMat.normalScale.x},\\nglanzFaktor: ${pbrMat.roughness},\\nmetallEffekt: ${pbrMat.metalness},\\nlichtStaerke: ${spot.intensity},\\nenvIntensitaet: ${pbrMat.envMapIntensity},\\nenvBlur: ${scene.backgroundBlurriness}`; navigator.clipboard.writeText(cfg); const b=e.target; b.textContent="Kopiert!"; setTimeout(()=>b.textContent="Copy Config",1500); };',
    'function dlBlob(blob,name){ const a=document.createElement("a"); a.href=URL.createObjectURL(blob); a.download=name; a.click(); }',
    'document.getElementById("btn-png").onclick=()=>{ renderer.render(scene,camera); renderer.domElement.toBlob((b)=>dlBlob(b,`pbr_${shapeType}_preview.png`)); };',
    'function createBakedGroup(){ const cloneGrp=artGroup.clone(); const bakedMesh=cloneGrp.children.at(0); const g=mesh.geometry.clone(); const pos=g.attributes.position; const nrm=g.attributes.normal; const uv=g.attributes.uv; const img=texStore.depth?.image;',
    '  if(img && pbrMat.displacementScale>0){ const c=document.createElement("canvas"); c.width=img.width; c.height=img.height; const ctx=c.getContext("2d"); ctx.drawImage(img,0,0); const data=ctx.getImageData(0,0,c.width,c.height).data;',
    '    for(let i=0;i<pos.count;i++){ const rawU=uv.getX(i), rawV=uv.getY(i); const edX=Math.min(rawU,1-rawU), edY=Math.min(rawV,1-rawV), ed=Math.min(edX,edY); const t=Math.max(0,Math.min(1,ed/0.04)); const mask=t*t*(3-2*t);',
    '      const u=(rawU*uvTile)%1.0, v=(rawV*uvTile)%1.0;',
    '      const px=Math.min(c.width-1,Math.floor(u*c.width)), py=Math.min(c.height-1,Math.floor((1-v)*c.height)); const hVal=(data[(py*c.width+px)*4]/255.0)*pbrMat.displacementScale*mask;',
    '      pos.setXYZ(i, pos.getX(i)+nrm.getX(i)*hVal, pos.getY(i)+nrm.getY(i)*hVal, pos.getZ(i)+nrm.getZ(i)*hVal); }',
    '    pos.needsUpdate=true; g.computeVertexNormals(); }',
    '  bakedMesh.geometry=g; const expMat=pbrMat.clone(); expMat.displacementMap=null; expMat.displacementScale=0; bakedMesh.material=expMat; return cloneGrp; }',
    'document.getElementById("btn-exp").onclick=()=>{ const fmt=document.getElementById("sel-fmt").value; const expObj=createBakedGroup();',
    '  if(fmt==="glb"){ new GLTFExporter().parse(expObj,(res)=>dlBlob(new Blob([res],{type:"model/gltf-binary"}),`pbr_${shapeType}_baked.glb`),(err)=>console.error(err),{binary:true}); }',
    '  else { const txt=new OBJExporter().parse(expObj); dlBlob(new Blob([txt],{type:"text/plain"}),`pbr_${shapeType}_baked.obj`); } };',
    'window.addEventListener("resize",()=>{camera.aspect=window.innerWidth/window.innerHeight;camera.updateProjectionMatrix();renderer.setSize(window.innerWidth,window.innerHeight);});',
    'function anim(t){requestAnimationFrame(anim);if(auto){spot.position.x=Math.sin(t*0.00075)*3.4;spot.position.y=Math.cos(t*0.00055)*2.6;}controls.update();renderer.render(scene,camera);}requestAnimationFrame(anim);',
    '</script></body></html>'
]

with open(os.path.join(_web_dir, "viewer.html"), "w", encoding="utf-8") as f:
    f.write("\n".join(VIEWER_HTML))
class FullPBRThreeJSPreview:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                # 1. Base Color / Albedo De-Lighting
                "delight_strength": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05}),
                # 2. Depth Map Parameter
                "depth_contrast": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 4.0, "step": 0.05}),
                "depth_smoothness": ("INT", {"default": 1, "min": 0, "max": 15, "step": 1}),
                "invert_depth": ("BOOLEAN", {"default": False}),
                # 3. Normal Map Parameter
                "normal_strength": ("FLOAT", {"default": 2.0, "min": 0.0, "max": 20.0, "step": 0.1}),
                "normal_blur": ("INT", {"default": 0, "min": 0, "max": 10, "step": 1}),
                "detail_mix": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.05}),
                "invert_normal_y": ("BOOLEAN", {"default": False}),
                # 4. Roughness Map Parameter
                "roughness_base": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.02}),
                "roughness_contrast": ("FLOAT", {"default": 1.2, "min": 0.1, "max": 4.0, "step": 0.05}),
                "invert_roughness": ("BOOLEAN", {"default": True}),
                # 5. Metalness Map Parameter
                "metalness_threshold": ("FLOAT", {"default": 0.65, "min": 0.0, "max": 1.0, "step": 0.02}),
                "metalness_strength": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05}),
                # 6. Ambient Occlusion Parameter
                "ao_strength": ("FLOAT", {"default": 1.2, "min": 0.0, "max": 3.0, "step": 0.05}),
                "ao_radius": ("INT", {"default": 8, "min": 1, "max": 25, "step": 1}),
            },
            "optional": {
                "height_depth": ("IMAGE",),
                "normal_map": ("IMAGE",),
                "roughness_map": ("IMAGE",),
                "metalness_map": ("IMAGE",),
                "ao_map": ("IMAGE",),
                "env_map": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("base_color", "depth_map", "normal_map", "roughness_map", "metalness_map", "ao_map")
    FUNCTION = "process_and_preview"
    OUTPUT_NODE = True
    CATEGORY = "3D/Preview"
    DESCRIPTION = "Generates full PBR maps (Albedo, Depth, Normal, Roughness, Metalness, AO) from a single image with an interactive Three.js 3D preview, UV tiling, Kelvin lighting presets, EXR/HDRI environment support, and baked GLB/OBJ export."

    def _save_tensor(self, tensor, filename, temp_dir):
        first_img = next(iter(tensor))
        img_np = np.clip(255.0 * first_img.cpu().numpy(), 0, 255).astype(np.uint8)
        img = Image.fromarray(img_np)
        img.save(os.path.join(temp_dir, filename))
        return filename

    def _sobel_normals(self, height_map, strength, invert_y):
        h_pad = F.pad(height_map.unsqueeze(1), (1, 1, 1, 1), mode="replicate").squeeze(1)
        dx = (h_pad[:, 1:-1, 2:] - h_pad[:, 1:-1, :-2]) * 0.5 * strength
        dy = (h_pad[:, 2:, 1:-1] - h_pad[:, :-2, 1:-1]) * 0.5 * strength
        nx = -dx
        ny = dy if invert_y else -dy
        nz = torch.ones_like(nx)
        norm = torch.sqrt(nx**2 + ny**2 + nz**2 + 1e-8)
        return nx / norm, ny / norm, nz / norm

    def process_and_preview(
        self,
        image,
        delight_strength=0.0,
        depth_contrast=1.0,
        depth_smoothness=1,
        invert_depth=False,
        normal_strength=2.0,
        normal_blur=0,
        detail_mix=0.35,
        invert_normal_y=False,
        roughness_base=0.5,
        roughness_contrast=1.2,
        invert_roughness=True,
        metalness_threshold=0.65,
        metalness_strength=0.0,
        ao_strength=1.2,
        ao_radius=8,
        height_depth=None,
        normal_map=None,
        roughness_map=None,
        metalness_map=None,
        ao_map=None,
        env_map=None,
        **kwargs,
    ):
        r = image[..., 0]
        g = image[..., 1]
        b = image[..., 2]
        height = 0.2126 * r + 0.7152 * g + 0.0722 * b

        # 1. Albedo De-Lighting (entfernt eingebrannte Schatten/Highlights aus Base Color)
        if delight_strength > 0.0:
            lum_4d = height.unsqueeze(1)
            local_avg = F.avg_pool2d(F.pad(lum_4d, (16, 16, 16, 16), mode="replicate"), 33, stride=1).squeeze(1)
            gain = (0.5 / (local_avg + 0.15)).clamp(0.4, 2.2)
            delit = torch.clamp(image * gain.unsqueeze(-1), 0.0, 1.0)
            base_color_out = torch.lerp(image, delit, delight_strength)
        else:
            base_color_out = image

        # 2. Depth / Height Map
        d_work = height
        if depth_smoothness > 0:
            d_4d = d_work.unsqueeze(1)
            k = depth_smoothness * 2 + 1
            d_work = F.avg_pool2d(d_4d, kernel_size=k, stride=1, padding=depth_smoothness).squeeze(1)

        d_work = torch.clamp((d_work - 0.5) * depth_contrast + 0.5, 0.0, 1.0)
        depth = (1.0 - d_work) if invert_depth else d_work
        depth_map_out = depth.unsqueeze(-1).repeat(1, 1, 1, 3)

        # 3. Normal Map (Makro-Form + Mikro-Detail-Mix)
        n_macro = depth
        if normal_blur > 0:
            n_4d = n_macro.unsqueeze(1)
            nk = normal_blur * 2 + 1
            n_macro = F.avg_pool2d(n_4d, kernel_size=nk, stride=1, padding=normal_blur).squeeze(1)

        mx, my, mz = self._sobel_normals(n_macro, normal_strength, invert_normal_y)
        if detail_mix > 0.0:
            fx, fy, fz = self._sobel_normals(height, normal_strength * 0.75, invert_normal_y)
            nx = mx + fx * detail_mix
            ny = my + fy * detail_mix
            nz = mz + fz * detail_mix
            norm = torch.sqrt(nx**2 + ny**2 + nz**2 + 1e-8)
            nx, ny, nz = nx / norm, ny / norm, nz / norm
        else:
            nx, ny, nz = mx, my, mz

        normal_map_out = torch.stack([nx * 0.5 + 0.5, ny * 0.5 + 0.5, nz * 0.5 + 0.5], dim=-1)

        # 4. Roughness Map (mit einstellbarer Basis-Rauheit & Kontrast)
        rough_src = (1.0 - depth) if invert_roughness else depth
        rough = torch.clamp((rough_src - 0.5) * roughness_contrast + roughness_base, 0.0, 1.0)
        roughness_map_out = rough.unsqueeze(-1).repeat(1, 1, 1, 3)

        # 5. Metalness Map
        max_c = torch.max(image[..., :3], dim=-1).values
        min_c = torch.min(image[..., :3], dim=-1).values
        sat = (max_c - min_c) / (max_c + 1e-6)
        metal_raw = torch.clamp((height - metalness_threshold) / max(1e-4, 1.0 - metalness_threshold), 0.0, 1.0)
        metal = torch.clamp(metal_raw * (1.0 - sat * 0.35) * metalness_strength, 0.0, 1.0)
        metalness_map_out = metal.unsqueeze(-1).repeat(1, 1, 1, 3)

        # 6. Multi-Scale Ambient Occlusion
        ao_4d = depth.unsqueeze(1)
        r_small = max(1, ao_radius // 2)
        r_large = max(2, ao_radius)
        blur_small = F.avg_pool2d(F.pad(ao_4d, (r_small, r_small, r_small, r_small), mode="replicate"), r_small * 2 + 1, stride=1).squeeze(1)
        blur_large = F.avg_pool2d(F.pad(ao_4d, (r_large, r_large, r_large, r_large), mode="replicate"), r_large * 2 + 1, stride=1).squeeze(1)
        cavity = torch.clamp((blur_small - depth) * 0.6 + (blur_large - depth) * 0.4, 0.0, 1.0)
        ao = torch.clamp(1.0 - cavity * ao_strength * 3.0, 0.0, 1.0)
        ao_map_out = ao.unsqueeze(-1).repeat(1, 1, 1, 3)

        active_depth = height_depth if height_depth is not None else depth_map_out
        active_normal = normal_map if normal_map is not None else normal_map_out
        active_roughness = roughness_map if roughness_map is not None else roughness_map_out
        active_metalness = metalness_map if metalness_map is not None else metalness_map_out
        active_ao = ao_map if ao_map is not None else ao_map_out

        if env_map is None and "env_map_image" in kwargs:
            env_map = kwargs.get("env_map_image")

        temp_dir = folder_paths.get_temp_directory()
        files = {
            "base": self._save_tensor(base_color_out, "pbr_full_base.png", temp_dir),
            "depth": self._save_tensor(active_depth, "pbr_full_depth.png", temp_dir),
            "normal": self._save_tensor(active_normal, "pbr_full_normal.png", temp_dir),
            "roughness": self._save_tensor(active_roughness, "pbr_full_roughness.png", temp_dir),
            "metalness": self._save_tensor(active_metalness, "pbr_full_metalness.png", temp_dir),
            "ao": self._save_tensor(active_ao, "pbr_full_ao.png", temp_dir),
        }

        if env_map is not None:
            files["env"] = self._save_tensor(env_map, "pbr_full_env.png", temp_dir)

        return {
            "ui": {"pbr_files": [files]},
            "result": (base_color_out, depth_map_out, normal_map_out, roughness_map_out, metalness_map_out, ao_map_out),
        }


NODE_CLASS_MAPPINGS = {
    "FullPBRThreeJSPreview": FullPBRThreeJSPreview
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FullPBRThreeJSPreview": "PBR Material Generator"
}

