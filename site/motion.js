/* Progressive enhancement: the complete report stays readable without JS. */
(() => {
  "use strict";
  const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
  const button = document.querySelector("[data-motion-toggle]");
  const progress = document.querySelector("[data-reading-progress]");
  const animations = new Set();
  let paused = false;
  let framePending = false;
  const allowed = () => !paused && !preference.matches;

  function syncMotion() {
    document.documentElement.classList.toggle("motion-paused", !allowed());
    if (!allowed()) {
      animations.forEach(animation => animation.cancel());
      animations.clear();
    }
    if (button) {
      button.hidden = false;
      button.disabled = preference.matches;
      button.setAttribute("aria-pressed", String(allowed()));
      button.textContent = preference.matches ? "Movimiento reducido" : paused ? "Activar animaciones" : "Pausar animaciones";
    }
  }

  function show(element) {
    if (!allowed() || typeof element.animate !== "function") return;
    // Move whole panels, never chart coordinates, axes, or numerical values.
    const animation = element.animate(
      [{ opacity: 0.65, transform: "translateY(12px)" }, { opacity: 1, transform: "translateY(0)" }],
      { duration: 420, easing: "cubic-bezier(.2,.65,.3,1)", iterations: 1 }
    );
    animations.add(animation);
    animation.onfinish = () => animations.delete(animation);
    animation.oncancel = () => animations.delete(animation);
  }

  function updateProgress() {
    framePending = false;
    if (!progress) return;
    const total = document.documentElement.scrollHeight - window.innerHeight;
    const fraction = total > 0 ? Math.min(1, Math.max(0, window.scrollY / total)) : 0;
    progress.style.transform = `scaleX(${fraction})`;
  }
  function queueProgress() {
    if (!framePending) {
      framePending = true;
      window.requestAnimationFrame(updateProgress);
    }
  }

  syncMotion();
  button?.addEventListener("click", () => { paused = !paused; syncMotion(); });
  preference.addEventListener?.("change", syncMotion);
  if (typeof window.IntersectionObserver === "function") {
    const observer = new window.IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        show(entry.target);
      });
    }, { threshold: 0.12 });
    document.querySelectorAll(".hero-copy, .hero-stat, .takeaway, .chart-card, .territory-panel, .section-head")
      .forEach(element => observer.observe(element));
  }
  window.addEventListener("scroll", queueProgress, { passive: true });
  window.addEventListener("resize", queueProgress, { passive: true });
  document.addEventListener("toggle", queueProgress, true);
  updateProgress();
})();
