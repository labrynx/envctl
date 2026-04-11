/* envctl — core helpers */

(function () {
  "use strict";

  window.envctl = window.envctl || {};

  window.envctl.state = {
    prefersReducedMotion: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  };

  window.envctl.utils = {
    safeLocalStorageGet: function (key) {
      try {
        return localStorage.getItem(key);
      } catch (_error) {
        return null;
      }
    },

    safeLocalStorageSet: function (key, value) {
      try {
        localStorage.setItem(key, value);
      } catch (_error) {
        /* Ignore storage failures */
      }
    },

    copyTextWithFeedback: function (button, text, doneClass) {
      if (!button || !text) return;
      if (!navigator.clipboard || typeof navigator.clipboard.writeText !== "function") return;

      navigator.clipboard.writeText(text).then(function () {
        button.classList.add(doneClass);
        button.textContent = "Copied";

        window.setTimeout(function () {
          button.classList.remove(doneClass);
          button.textContent = "Copy";
        }, 1200);
      });
    },

    updateHeaderMetrics: function () {
      var root = document.documentElement;
      if (!root) return;

      var header = document.querySelector(".md-header");
      var tabs = document.querySelector(".md-tabs");
      var headerHeight = header ? header.offsetHeight : 0;
      var tabsHeight = 0;

      if (tabs) {
        var tabsStyle = window.getComputedStyle(tabs);
        var tabsVisible = tabsStyle.display !== "none" && tabsStyle.visibility !== "hidden";
        if (tabsVisible) {
          tabsHeight = tabs.offsetHeight;
        }
      }

      var totalHeight = headerHeight + tabsHeight;
      if (totalHeight > 0) {
        root.style.setProperty("--envctl-header-height", totalHeight + "px");
      }
    },
  };

  window.envctl.register = function (name, initFn) {
    if (!window.envctl.modules) {
      window.envctl.modules = [];
    }

    window.envctl.modules.push({
      name: name,
      init: initFn,
    });
  };

  window.envctl.utils.updateHeaderMetrics();

  if (!window.envctl._headerMetricsBound) {
    window.addEventListener("load", window.envctl.utils.updateHeaderMetrics, { passive: true });
    window.addEventListener("resize", window.envctl.utils.updateHeaderMetrics, { passive: true });

    if (typeof ResizeObserver === "function") {
      var observedNodes = [];
      var header = document.querySelector(".md-header");
      var tabs = document.querySelector(".md-tabs");

      if (header) observedNodes.push(header);
      if (tabs) observedNodes.push(tabs);

      if (observedNodes.length) {
        window.envctl._headerMetricsObserver = new ResizeObserver(function () {
          window.envctl.utils.updateHeaderMetrics();
        });

        observedNodes.forEach(function (node) {
          window.envctl._headerMetricsObserver.observe(node);
        });
      }
    }

    window.envctl._headerMetricsBound = true;
  }
})();
