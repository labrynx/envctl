const decorateExternalLinks = () => {
  const contentLinks = document.querySelectorAll(".md-content a[href]");

  for (const link of contentLinks) {
    const href = link.getAttribute("href");
    if (!href) continue;

    const isExternal =
      href.startsWith("http://") || href.startsWith("https://");

    if (!isExternal) continue;

    link.setAttribute("target", "_blank");
    link.setAttribute("rel", "noopener noreferrer");

    if (!link.querySelector(".envctl-external-link-marker")) {
      const marker = document.createElement("span");
      marker.className = "envctl-external-link-marker";
      marker.setAttribute("aria-hidden", "true");
      marker.textContent = " ↗";
      link.appendChild(marker);
    }
  }
};

let splashParallaxAttached = false;
let splashParallaxTicking = false;

const updateSplashParallax = () => {
  const splash = document.querySelector(".envctl-page--home");
  if (!splash) return;

  const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
  if (reducedMotion || window.innerWidth < 761) {
    splash.style.setProperty("--envctl-splash-shift", "0px");
    return;
  }

  const rect = splash.getBoundingClientRect();
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight;

  if (rect.bottom <= 0 || rect.top >= viewportHeight) {
    return;
  }

  const distance = Math.max(-120, Math.min(120, rect.top * -0.18));
  splash.style.setProperty("--envctl-splash-shift", `${distance}px`);
};

const requestSplashParallaxUpdate = () => {
  if (splashParallaxTicking) return;
  splashParallaxTicking = true;

  window.requestAnimationFrame(() => {
    updateSplashParallax();
    splashParallaxTicking = false;
  });
};

const setupSplashParallax = () => {
  if (splashParallaxAttached) {
    updateSplashParallax();
    return;
  }

  window.addEventListener("scroll", requestSplashParallaxUpdate, { passive: true });
  window.addEventListener("resize", requestSplashParallaxUpdate);
  splashParallaxAttached = true;
  updateSplashParallax();
};

const getMermaidConfig = () => {
  const scheme = document.body?.getAttribute("data-md-color-scheme") || "default";
  const isDark = scheme === "slate";

  if (isDark) {
    return {
      startOnLoad: false,
      theme: "base",
      securityLevel: "loose",
      flowchart: {
        curve: "basis",
        htmlLabels: false,
      },
      themeVariables: {
        background: "transparent",
        fontFamily:
          'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        primaryColor: "#1f2937",
        primaryTextColor: "#f3f4f6",
        primaryBorderColor: "#475569",
        secondaryColor: "#0f172a",
        secondaryTextColor: "#f3f4f6",
        secondaryBorderColor: "#475569",
        tertiaryColor: "#111827",
        tertiaryTextColor: "#e5e7eb",
        tertiaryBorderColor: "#475569",
        mainBkg: "#1f2937",
        nodeBorder: "#475569",
        lineColor: "#94a3b8",
        textColor: "#e5e7eb",
        edgeLabelBackground: "#111827",
      },
    };
  }

  return {
    startOnLoad: false,
    theme: "base",
    securityLevel: "loose",
    flowchart: {
      curve: "basis",
      htmlLabels: false,
    },
    themeVariables: {
      background: "transparent",
      fontFamily:
        'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      primaryColor: "#f8fafc",
      primaryTextColor: "#0f172a",
      primaryBorderColor: "#cbd5e1",
      secondaryColor: "#e2e8f0",
      secondaryTextColor: "#0f172a",
      secondaryBorderColor: "#cbd5e1",
      tertiaryColor: "#ffffff",
      tertiaryTextColor: "#0f172a",
      tertiaryBorderColor: "#cbd5e1",
      mainBkg: "#f8fafc",
      nodeBorder: "#cbd5e1",
      lineColor: "#334155",
      textColor: "#0f172a",
      edgeLabelBackground: "#ffffff",
    },
  };
};

const setupMermaid = () => {
  if (!window.mermaid) return;

  const config = getMermaidConfig();
  const scheme = document.body?.getAttribute("data-md-color-scheme") || "default";

  if (window.__envctlMermaidScheme === scheme) return;

  window.mermaid.initialize(config);
  window.__envctlMermaidScheme = scheme;
};

const renderMermaid = () => {
  if (!window.mermaid) return;

  setupMermaid();

  const nodes = document.querySelectorAll(".mermaid");
  if (!nodes.length) return;

  for (const node of nodes) {
    if (!node.dataset.mermaidSource) {
      node.dataset.mermaidSource = node.textContent.trim();
    }
    node.textContent = node.dataset.mermaidSource;
    node.removeAttribute("data-processed");
  }

  window.mermaid.run({ nodes });
};

const onContentReady = (callback) => {
  if (typeof document$ !== "undefined") {
    document$.subscribe(callback);
    return;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", callback, { once: true });
    return;
  }

  callback();
};

onContentReady(() => {
  decorateExternalLinks();
  renderMermaid();
  setupSplashParallax();
});

let mermaidThemeObserverAttached = false;

const observeThemeChanges = () => {
  if (mermaidThemeObserverAttached || !document.body) return;

  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (
        mutation.type === "attributes" &&
        mutation.attributeName === "data-md-color-scheme"
      ) {
        renderMermaid();
        break;
      }
    }
  });

  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ["data-md-color-scheme"],
  });

  mermaidThemeObserverAttached = true;
};

onContentReady(() => {
  observeThemeChanges();
});
