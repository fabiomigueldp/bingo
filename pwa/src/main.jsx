import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./styles.css";

function installIOSViewportGuards() {
  const scrollableSelector = [
    ".setup-content",
    ".call-card",
    ".history-list",
    ".boards-list",
    ".materials-list",
    ".teaching-scroll",
    ".rules-list",
    ".conference-scroll"
  ].join(", ");

  let startY = 0;
  let scrollTarget = null;

  function findScrollable(target) {
    const element = target instanceof Element ? target.closest(scrollableSelector) : null;
    if (!element) return null;
    return element.scrollHeight > element.clientHeight + 1 ? element : null;
  }

  function canScroll(element, deltaY) {
    if (!element) return false;
    if (deltaY < 0) return element.scrollTop > 0;
    if (deltaY > 0) return element.scrollTop + element.clientHeight < element.scrollHeight - 1;
    return false;
  }

  function prevent(event) {
    if (event.cancelable) event.preventDefault();
  }

  document.addEventListener(
    "touchstart",
    (event) => {
      if (event.touches.length !== 1) {
        scrollTarget = null;
        return;
      }
      startY = event.touches[0].clientY;
      scrollTarget = findScrollable(event.target);
    },
    { passive: true }
  );

  document.addEventListener(
    "touchmove",
    (event) => {
      if (event.touches.length !== 1) {
        prevent(event);
        return;
      }

      const currentY = event.touches[0].clientY;
      const deltaY = startY - currentY;
      if (!canScroll(scrollTarget, deltaY)) prevent(event);
    },
    { passive: false }
  );

  document.addEventListener("gesturestart", prevent, { passive: false });
  document.addEventListener("gesturechange", prevent, { passive: false });
  document.addEventListener("gestureend", prevent, { passive: false });
}

installIOSViewportGuards();

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {});
  });
}
