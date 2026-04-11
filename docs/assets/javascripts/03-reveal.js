/* envctl — reveal on scroll */

(function () {
  "use strict";

  window.envctl.register("reveal", function () {
    var revealItems = Array.from(document.querySelectorAll(".envctl-reveal"));
    if (!revealItems.length) return;

    if (window.envctl.state.prefersReducedMotion) {
      revealItems.forEach(function (item) {
        item.classList.add("envctl-reveal--visible");
      });
      return;
    }

    if ("IntersectionObserver" in window) {
      var revealObserver = new IntersectionObserver(
        function (entries, observer) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("envctl-reveal--visible");
            observer.unobserve(entry.target);
          });
        },
        {
          threshold: 0.12,
          rootMargin: "0px 0px -8% 0px",
        }
      );

      revealItems.forEach(function (item) {
        revealObserver.observe(item);
      });

      return;
    }

    revealItems.forEach(function (item) {
      item.classList.add("envctl-reveal--visible");
    });
  });
})();
