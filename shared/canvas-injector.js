/**
 * Canvas-to-Code + Visual Edit Layer (v2)
 * Injected into generated application bundles during development.
 *
 * - Hold Ctrl/Cmd + click → post source file + line to parent (target for AI)
 * - Single click while "visual edit mode" is active → open property panel data
 * - Highlights selected element and extracts text / className / basic styles
 */
(function () {
  if (typeof window === "undefined") return;

  let visualEditMode = false;
  let selectedEl = null;

  console.log(
    "%c🚀 Canvas-to-Code + Visual Edit active%c – Ctrl/Cmd+click to target · Enable visual mode from the editor for direct edits",
    "color:#3b82f6;font-weight:bold",
    "color:inherit"
  );

  window.addEventListener("message", (event) => {
    if (event.data?.type === "VISUAL_EDIT_MODE") {
      visualEditMode = !!event.data.enabled;
      document.body.style.cursor = visualEditMode ? "crosshair" : "";
      if (!visualEditMode && selectedEl) {
        clearHighlight(selectedEl);
        selectedEl = null;
      }
    }
  });

  function clearHighlight(el) {
    if (!el) return;
    el.style.outline = el.__canvas_prev_outline || "";
    el.style.outlineOffset = el.__canvas_prev_offset || "";
  }

  function applyHighlight(el) {
    el.__canvas_prev_outline = el.style.outline;
    el.__canvas_prev_offset = el.style.outlineOffset;
    el.style.outline = "2px solid #3b82f6";
    el.style.outlineOffset = "2px";
  }

  function extractSource(element) {
    let sourceMetadata = null;
    const fiberKey = Object.keys(element).find(
      (key) =>
        key.startsWith("__reactFiber$") ||
        key.startsWith("__reactInternalInstance$")
    );
    if (fiberKey && element[fiberKey]) {
      let inst = element[fiberKey];
      while (inst) {
        if (inst._debugSource) {
          sourceMetadata = {
            fileName: inst._debugSource.fileName,
            lineNumber: inst._debugSource.lineNumber,
          };
          break;
        }
        if (inst.elementType && inst.elementType._debugSource) {
          sourceMetadata = {
            fileName: inst.elementType._debugSource.fileName,
            lineNumber: inst.elementType._debugSource.lineNumber,
          };
          break;
        }
        inst = inst.return;
      }
    }
    if (!sourceMetadata) {
      const fileAttr =
        element.getAttribute("data-source-file") ||
        element.closest("[data-source-file]")?.getAttribute("data-source-file");
      const lineAttr =
        element.getAttribute("data-source-line") ||
        element.closest("[data-source-line]")?.getAttribute("data-source-line");
      if (fileAttr) {
        sourceMetadata = {
          fileName: fileAttr,
          lineNumber: parseInt(lineAttr || "1", 10),
        };
      }
    }
    if (sourceMetadata) {
      let filePath = sourceMetadata.fileName;
      if (filePath.includes("/src/")) {
        filePath = "src/" + filePath.split("/src/").pop();
      }
      return { filePath, line: sourceMetadata.lineNumber };
    }
    return null;
  }

  function getComputedBasics(el) {
    const cs = window.getComputedStyle(el);
    return {
      color: cs.color,
      backgroundColor: cs.backgroundColor,
      fontSize: cs.fontSize,
      fontWeight: cs.fontWeight,
      padding: cs.padding,
      margin: cs.margin,
      borderRadius: cs.borderRadius,
    };
  }

  window.addEventListener(
    "click",
    (event) => {
      const element = event.target;
      if (!element || element === document.documentElement || element === document.body)
        return;

      if (event.metaKey || event.ctrlKey) {
        event.preventDefault();
        event.stopPropagation();
        const src = extractSource(element);
        if (src) {
          window.parent.postMessage(
            {
              type: "VISUAL_CANVAS_SYNC",
              filePath: src.filePath,
              line: src.line,
            },
            "*"
          );
          const originalOutline = element.style.outline;
          const originalTransition = element.style.transition;
          element.style.transition = "outline 0.15s ease";
          element.style.outline = "2px solid #3b82f6";
          setTimeout(() => {
            element.style.outline = originalOutline;
            element.style.transition = originalTransition;
          }, 700);
        } else {
          console.warn(
            "[Canvas Sync] Could not map DOM node to source. Run in React dev mode."
          );
        }
        return;
      }

      if (visualEditMode) {
        event.preventDefault();
        event.stopPropagation();
        if (selectedEl) clearHighlight(selectedEl);
        selectedEl = element;
        applyHighlight(element);
        const src = extractSource(element) || {
          filePath: "src/App.tsx",
          line: null,
        };
        const text = (element.innerText || element.textContent || "").trim().slice(0, 200);
        const className = element.className?.toString?.() || "";
        window.parent.postMessage(
          {
            type: "VISUAL_EDIT_SELECT",
            filePath: src.filePath,
            line: src.line,
            tag: element.tagName.toLowerCase(),
            text,
            className,
            styles: getComputedBasics(element),
            selector: element.id
              ? `#${element.id}`
              : element.className
              ? `.${String(element.className).split(/\s+/)[0]}`
              : element.tagName.toLowerCase(),
          },
          "*"
        );
      }
    },
    true
  );
})();
