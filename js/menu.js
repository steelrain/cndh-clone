(function () {
  var gnb = document.getElementById("gnb");
  var wrap = document.getElementById("gnb_wrap");
  var lists = gnb ? gnb.querySelectorAll(":scope > li > ul") : [];
  var narrow = window.matchMedia("(max-width: 390px)");
  var toggle = null;

  function setMenu(open) {
    if (narrow.matches) return;
    for (var i = 0; i < lists.length; i++) {
      lists[i].style.display = open ? "block" : "none";
    }
    if (wrap) wrap.style.height = open ? "268px" : "0px";
  }

  function ensureToggle() {
    if (!narrow.matches) {
      document.body.classList.remove("nav-open");
      if (toggle && toggle.parentNode) toggle.parentNode.removeChild(toggle);
      toggle = null;
      return;
    }
    if (toggle) return;
    toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "nav_toggle";
    toggle.setAttribute("aria-expanded", "false");
    toggle.textContent = "메뉴";
    var host = document.querySelector(".section_02_w") || document.getElementById("header");
    if (host) host.insertBefore(toggle, host.firstChild);
    toggle.addEventListener("click", function () {
      var open = !document.body.classList.contains("nav-open");
      document.body.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  function syncLayout() {
    ensureToggle();
    if (!narrow.matches) setMenu(false);
  }

  syncLayout();
  if (gnb) {
    gnb.addEventListener("mouseenter", function () { setMenu(true); });
    gnb.addEventListener("mouseleave", function () { setMenu(false); });
  }

  var familyBtn = document.getElementById("family_site_open");
  var familyMenu = document.getElementById("famliy_site_menu");
  document.body.addEventListener("click", function (event) {
    if (!familyMenu || !familyBtn) return;
    if (familyBtn.contains(event.target)) familyMenu.style.display = "block";
    else familyMenu.style.display = "none";
  });

  var quick = document.querySelector(".quick_area");
  var quickTop = 330;
  function placeQuick() {
    if (!quick) return;
    if (narrow.matches) {
      quick.style.top = "";
      return;
    }
    quick.style.top = (window.scrollY || document.documentElement.scrollTop) + quickTop + "px";
  }
  if (quick) {
    placeQuick();
    window.addEventListener("scroll", placeQuick);
  }
  if (narrow.addEventListener) {
    narrow.addEventListener("change", function () {
      syncLayout();
      placeQuick();
    });
  }
})();
