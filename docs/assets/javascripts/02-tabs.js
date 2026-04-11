/* envctl — accessible CLI tabs */

(function () {
  "use strict";

  window.envctl.register("tabs", function () {
    var tabs = Array.from(document.querySelectorAll(".envctl-cli__tab"));
    var panels = Array.from(document.querySelectorAll(".envctl-cli__panel"));
    var storageKey = "envctl-active-tab";

    if (!tabs.length || !panels.length) return;

    function activateTab(targetTab, shouldFocus) {
      if (!targetTab) return;

      var target = targetTab.getAttribute("data-tab");
      if (!target) return;

      tabs.forEach(function (tab) {
        var isActive = tab === targetTab;
        tab.classList.toggle("envctl-cli__tab--active", isActive);
        tab.setAttribute("aria-selected", isActive ? "true" : "false");
        tab.setAttribute("tabindex", isActive ? "0" : "-1");
      });

      panels.forEach(function (panel) {
        var isActive = panel.getAttribute("data-panel") === target;
        panel.classList.toggle("envctl-cli__panel--active", isActive);
        panel.hidden = !isActive;
      });

      window.envctl.utils.safeLocalStorageSet(storageKey, target);

      if (shouldFocus) {
        targetTab.focus();
      }
    }

    tabs.forEach(function (tab, index) {
      if (tab.dataset.envctlTabsBound === "true") return;
      tab.dataset.envctlTabsBound = "true";

      tab.addEventListener("click", function () {
        activateTab(tab, false);
      });

      tab.addEventListener("keydown", function (event) {
        var nextIndex = null;

        if (event.key === "ArrowRight") {
          nextIndex = (index + 1) % tabs.length;
        } else if (event.key === "ArrowLeft") {
          nextIndex = (index - 1 + tabs.length) % tabs.length;
        } else if (event.key === "Home") {
          nextIndex = 0;
        } else if (event.key === "End") {
          nextIndex = tabs.length - 1;
        }

        if (nextIndex !== null) {
          event.preventDefault();
          activateTab(tabs[nextIndex], true);
        }
      });
    });

    var initialTabName = window.envctl.utils.safeLocalStorageGet(storageKey);

    var initialTab =
      tabs.find(function (tab) {
        return tab.getAttribute("data-tab") === initialTabName;
      }) ||
      tabs.find(function (tab) {
        return tab.classList.contains("envctl-cli__tab--active");
      }) ||
      tabs[0];

    if (initialTab) {
      activateTab(initialTab, false);
    }
  });
})();