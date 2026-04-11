/* envctl — header state on scroll */

(function () {
  "use strict";

  window.envctl.register("header", function () {
    var header = document.querySelector(".md-header");
    if (!header) return;

    function updateHeaderState() {
      if (window.scrollY > 12) {
        header.classList.add("envctl-header--scrolled");
      } else {
        header.classList.remove("envctl-header--scrolled");
      }
    }

    updateHeaderState();

    if (!window.envctl._headerScrollBound) {
      window.addEventListener("scroll", updateHeaderState, { passive: true });
      window.envctl._headerScrollBound = true;
    }
  });
})();