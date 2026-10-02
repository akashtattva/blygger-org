/* Jump Links drawer: toggles .is-open on the nav and scrim in
   templates/page.html. TRANSITION_MS must match the 0.4s transform
   curve in site.css. Drag dismiss: half the drawer height, or a fast
   downward flick. No dependencies. */
(() => {
  const OPEN_ATTR = "data-jump-links-open";
  const DRAWER_ATTR = "data-jump-links";
  const SCRIM_ATTR = "data-jump-links-scrim";
  const CLOSE_ATTR = "data-jump-links-close";
  const GRIP_ATTR = "data-jump-links-grip";
  const OPEN_CLASS = "is-open";
  const TRANSITION_MS = 400;
  const DISMISS_FRACTION = 0.5;
  const DISMISS_VELOCITY_PX_S = 600;

  let closeTimeoutId = null;
  let dragState = null;

  function clearCloseTimeout() {
    if (closeTimeoutId !== null) {
      window.clearTimeout(closeTimeoutId);
      closeTimeoutId = null;
    }
  }

  function prefersReducedMotion() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function triggerFor(drawer) {
    const id = drawer.id;
    if (!id) return null;
    return document.querySelector(`[${OPEN_ATTR}][aria-controls="${id}"]`);
  }

  function scrimFor(drawer) {
    return drawer.parentElement?.querySelector(`[${SCRIM_ATTR}]`) ?? null;
  }

  function openDrawer(drawer) {
    clearCloseTimeout();
    drawer.toggleAttribute("inert", false);
    drawer.classList.add(OPEN_CLASS);
    scrimFor(drawer)?.classList.add(OPEN_CLASS);
    const trigger = triggerFor(drawer);
    trigger?.setAttribute("aria-expanded", "true");
    drawer.querySelector(`[${CLOSE_ATTR}]`)?.focus({ preventScroll: true });
  }

  function closeDrawer(drawer) {
    clearCloseTimeout();
    dragState = null;
    drawer.classList.remove(OPEN_CLASS);
    scrimFor(drawer)?.classList.remove(OPEN_CLASS);
    const trigger = triggerFor(drawer);
    trigger?.setAttribute("aria-expanded", "false");
    void drawer.offsetHeight;
    drawer.style.transition = "";
    drawer.style.transform = "";
    closeTimeoutId = window.setTimeout(() => {
      drawer.toggleAttribute("inert", true);
      closeTimeoutId = null;
    }, TRANSITION_MS);
    trigger?.focus({ preventScroll: true });
  }

  function flickVelocity() {
    if (!dragState || dragState.samples.length < 2) return 0;
    const samples = dragState.samples;
    const last = samples[samples.length - 1];
    const cutoff = last.t - 120;
    let first = samples[0];
    for (const sample of samples) {
      if (sample.t >= cutoff) {
        first = sample;
        break;
      }
    }
    const dt = last.t - first.t;
    if (dt <= 0) return 0;
    return ((last.y - first.y) / dt) * 1000;
  }

  function init() {
    const drawer = document.querySelector(`[${DRAWER_ATTR}]`);
    if (!drawer) return;
    const trigger = triggerFor(drawer);
    if (!trigger) return;
    const root = drawer.closest(".jump-links");
    // No headings → empty list → keep the control hidden (CSS also gates this).
    if (root && !root.querySelector("li")) return;
    const grip = drawer.querySelector(`[${GRIP_ATTR}]`) ?? drawer;

    trigger.addEventListener("click", () => {
      if (drawer.classList.contains(OPEN_CLASS)) {
        closeDrawer(drawer);
      } else {
        openDrawer(drawer);
      }
    });

    drawer.querySelector(`[${CLOSE_ATTR}]`)?.addEventListener("click", () => {
      closeDrawer(drawer);
    });

    scrimFor(drawer)?.addEventListener("click", () => {
      closeDrawer(drawer);
    });

    drawer.querySelectorAll('a[href^="#"]').forEach((link) => {
      link.addEventListener("click", () => {
        closeDrawer(drawer);
      });
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && drawer.classList.contains(OPEN_CLASS)) {
        closeDrawer(drawer);
      }
    });

    grip.addEventListener("pointerdown", (event) => {
      if (
        !event.isPrimary ||
        !drawer.classList.contains(OPEN_CLASS) ||
        prefersReducedMotion()
      ) {
        return;
      }
      dragState = {
        startY: event.clientY,
        samples: [{ y: 0, t: performance.now() }],
        pointerId: event.pointerId,
      };
      try {
        grip.setPointerCapture(event.pointerId);
      } catch {
        // Moves still track while the pointer stays over the grip.
      }
      drawer.style.transition = "none";
    });

    grip.addEventListener("pointermove", (event) => {
      if (!dragState || event.pointerId !== dragState.pointerId) return;
      const offset = Math.max(0, event.clientY - dragState.startY);
      dragState.samples.push({ y: offset, t: performance.now() });
      drawer.style.transform = `translateY(${offset}px)`;
    });

    const endDrag = (event) => {
      if (!dragState || event.pointerId !== dragState.pointerId) return;
      const offset = Math.max(0, event.clientY - dragState.startY);
      const velocity = flickVelocity();
      dragState = null;
      if (!drawer.classList.contains(OPEN_CLASS)) {
        drawer.style.transition = "";
        drawer.style.transform = "";
        return;
      }
      const dismiss =
        offset > drawer.offsetHeight * DISMISS_FRACTION ||
        velocity > DISMISS_VELOCITY_PX_S;
      if (dismiss) {
        drawer.style.transition = "";
        closeDrawer(drawer);
      } else {
        drawer.style.transition = "";
        drawer.style.transform = "";
      }
    };

    grip.addEventListener("pointerup", endDrag);
    grip.addEventListener("pointercancel", endDrag);
  }

  init();
})();
