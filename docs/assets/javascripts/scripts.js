/* envctl — scripts.js
   Entry point */

(function () {
  "use strict";

  function runEnvctlModules() {
    if (!window.envctl || !Array.isArray(window.envctl.modules)) return;

    window.envctl.modules.forEach(function (moduleDef) {
      if (!moduleDef || typeof moduleDef.init !== "function") return;

      try {
        moduleDef.init();
      } catch (error) {
        console.error("[envctl] Failed to initialize module:", moduleDef.name, error);
      }
    });
  }

  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(function () {
      runEnvctlModules();
    });
  } else {
    document.addEventListener("DOMContentLoaded", function () {
      runEnvctlModules();
    });
  }
})();
