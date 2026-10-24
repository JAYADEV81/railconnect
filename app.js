document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("navToggle");
  const menu = document.getElementById("navMenu");
  if (toggle && menu) {
    toggle.addEventListener("click", () => {
      const expanded = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!expanded));
      menu.classList.toggle("open");
    });
  }

  const from = document.getElementById("from");
  const to = document.getElementById("to");
  const swap = document.getElementById("swapStations");
  if (swap && from && to) {
    swap.addEventListener("click", () => {
      const oldFrom = from.value;
      from.value = to.value;
      to.value = oldFrom;
    });
  }

  const bookingForm = document.getElementById("bookingForm");
  if (bookingForm && typeof window.RAIL_FARE !== "undefined") {
    const classSelect = document.getElementById("travel_class");
    const seatsInput = document.getElementById("seats");
    const fareEstimate = document.getElementById("fareEstimate");
    const fareTotal = document.getElementById("fareTotal");
    const classLabel = document.getElementById("classLabel");
    const seatLabel = document.getElementById("seatLabel");
    const multipliers = { SL: 1, "3A": 2.1, "2A": 3, "1A": 4.5, CC: 1.6 };
    const updateFare = () => {
      const cls = classSelect.value;
      const count = Math.max(1, Math.min(6, Number(seatsInput.value) || 1));
      const total = Math.round(window.RAIL_FARE * (multipliers[cls] || 1) * count * 100) / 100;
      const formatted = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(total);
      fareEstimate.textContent = formatted;
      fareTotal.textContent = formatted;
      classLabel.textContent = cls;
      seatLabel.textContent = count;
    };
    classSelect.addEventListener("change", updateFare);
    seatsInput.addEventListener("input", updateFare);
    updateFare();
  }

  document.querySelectorAll("[data-copy]").forEach(button => {
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(button.dataset.copy);
        button.textContent = "Copied!";
      } catch {
        button.textContent = button.dataset.copy;
      }
    });
  });
});
