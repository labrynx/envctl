/* envctl — copy buttons for terminals */

(function () {
  "use strict";

  function extractLandingTerminalCommands(block) {
    return Array.from(block.querySelectorAll(".envctl-code-line"))
      .map(function (line) {
        var text = line.textContent || "";
        return text.replace(/^\s*\d+\s*/, "");
      })
      .map(function (line) {
        return line.trim();
      })
      .filter(function (line) {
        return line.startsWith("$");
      })
      .map(function (line) {
        return line.replace(/^\$\s*/, "");
      })
      .join("\n");
  }

  function extractDocsTerminalCommands(body) {
    return Array.from(body.querySelectorAll(".envctl-doc-terminal__line"))
      .map(function (line) {
        return (line.textContent || "").trimEnd();
      })
      .filter(function (line) {
        return line.trim().startsWith("$");
      })
      .map(function (line) {
        return line.replace(/^\$\s*/, "");
      })
      .join("\n");
  }

  function initLandingTerminalCopy() {
    document.querySelectorAll(".envctl-terminal").forEach(function (terminal) {
      var bar = terminal.querySelector(".envctl-terminal__bar");
      var code = terminal.querySelector(".envctl-terminal__code");
      if (!bar || !code) return;

      if (bar.querySelector(".envctl-terminal__copy")) return;

      var copyButton = document.createElement("button");
      copyButton.type = "button";
      copyButton.className = "envctl-terminal__copy";
      copyButton.setAttribute("aria-label", "Copy terminal commands");
      copyButton.textContent = "Copy";

      copyButton.addEventListener("click", function () {
        var text = extractLandingTerminalCommands(code);
        window.envctl.utils.copyTextWithFeedback(copyButton, text, "envctl-terminal__copy--done");
      });

      bar.appendChild(copyButton);
    });
  }

  function initDocsTerminalCopy() {
    document.querySelectorAll(".envctl-doc-terminal").forEach(function (terminal) {
      var bar = terminal.querySelector(".envctl-doc-terminal__bar");
      var body = terminal.querySelector(".envctl-doc-terminal__body");
      if (!bar || !body) return;

      if (bar.querySelector(".envctl-doc-terminal__copy")) return;

      var copyButton = document.createElement("button");
      copyButton.type = "button";
      copyButton.className = "envctl-doc-terminal__copy";
      copyButton.setAttribute("aria-label", "Copy terminal commands");
      copyButton.textContent = "Copy";

      copyButton.addEventListener("click", function () {
        var text = extractDocsTerminalCommands(body);
        window.envctl.utils.copyTextWithFeedback(copyButton, text, "envctl-doc-terminal__copy--done");
      });

      bar.appendChild(copyButton);
    });
  }

  window.envctl.register("copy", function () {
    initLandingTerminalCopy();
    initDocsTerminalCopy();
  });
})();
