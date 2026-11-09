// Hover/focus tooltip for the citations-per-year chart.
document.querySelectorAll(".chart-wrap").forEach((wrap) => {
  const svg = wrap.querySelector("svg");
  const tip = wrap.querySelector(".tooltip");
  const clear = () => wrap.querySelectorAll(".bar.active").forEach((b) => b.classList.remove("active"));

  const show = (bar) => {
    clear();
    bar.classList.add("active");
    tip.textContent = `${bar.dataset.year}: ${bar.dataset.count} citations`;
    tip.style.left = `${bar.dataset.left}%`;
    tip.style.top = `${bar.dataset.top}%`;
    tip.hidden = false;
  };
  const hide = () => {
    tip.hidden = true;
    clear();
  };

  wrap.querySelectorAll(".bar").forEach((bar) => {
    bar.addEventListener("mouseenter", () => show(bar));
    bar.addEventListener("focus", () => show(bar));
    bar.addEventListener("blur", hide);
  });
  svg.addEventListener("mouseleave", hide);
});
