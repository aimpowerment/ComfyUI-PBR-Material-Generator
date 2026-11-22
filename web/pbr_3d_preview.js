import { app } from "../../scripts/app.js";
app.registerExtension({
  name: "Comfy.FullPBRThreeJSPreview",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "FullPBRThreeJSPreview") return;
    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      if (onNodeCreated) onNodeCreated.apply(this, arguments);
      const node = this;
      const container = document.createElement("div");
      container.style.cssText = "width:100%;height:100%;min-height:260px;background:#141417;border-radius:6px;overflow:hidden;position:relative;box-sizing:border-box;";
      const iframe = document.createElement("iframe");
      iframe.style.cssText = "position:absolute;inset:0;width:100%;height:100%;border:none;display:block;";
      container.appendChild(iframe);
      const widget = this.addDOMWidget("threejs_pbr_viewer", "preview", container, {
        getMinHeight: () => 260,
        hideOnZoom: false,
      });
      widget.computeSize = (width) => Array.of(width, 380);
      const onDrawForeground = this.onDrawForeground;
      this.onDrawForeground = function (ctx) {
        if (onDrawForeground) onDrawForeground.apply(this, arguments);
        if (widget.last_y !== undefined && node.size) {
          const availH = Math.max(260, node.size.at(1) - widget.last_y - 12);
          if (container.style.height !== availH + "px") container.style.height = availH + "px";
        }
      };
      this.setSize(Array.of(640, 880));
      this.previewIframe = iframe;
    };
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
      if (onExecuted) onExecuted.apply(this, arguments);
      const f = message?.pbr_files?.at(0);
      if (!f || !this.previewIframe) return;
      const params = new URLSearchParams({ v: "23", t: Date.now(), ...f });
      this.previewIframe.src = "/extensions/ComfyUI_PBR_Preview/viewer.html?" + params.toString();
    };
  }
});
