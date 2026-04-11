/* envctl — back to top button */

(function () {
  "use strict";

  function updateBackToTop() {
    var backToTop = document.querySelector(".envctl-backtotop");
    if (!backToTop) return;

    if (window.scrollY > 480) {
      backToTop.classList.add("envctl-backtotop--visible");
    } else {
      backToTop.classList.remove("envctl-backtotop--visible");
    }
  }

  window.envctl.register("backtotop", function () {
    var backToTop = document.querySelector(".envctl-backtotop");

    if (!backToTop) {
      backToTop = document.createElement("button");
      backToTop.type = "button";
      backToTop.className = "envctl-backtotop";
      backToTop.setAttribute("aria-label", "Back to top");
      backToTop.textContent = "↑ Top";
      document.body.appendChild(backToTop);
    }

    if (!backToTop.dataset.envctlClickBound) {
      backToTop.addEventListener("click", function () {
        window.scrollTo({
          top: 0,
          behavior: window.envctl.state.prefersReducedMotion ? "auto" : "smooth",
        });
      });

      backToTop.dataset.envctlClickBound = "true";
    }

    updateBackToTop();

    if (!window.envctl._backToTopScrollBound) {
      window.addEventListener("scroll", updateBackToTop, { passive: true });
      window.envctl._backToTopScrollBound = true;
    }
  });
})();
