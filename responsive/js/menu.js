(function () {
  var toggle = document.querySelector(".nav_toggle");
  var wide = window.matchMedia("(min-width: 1024px)");
  var familyBtn = document.getElementById("family_site_open");
  var familyMenu = document.getElementById("famliy_site_menu");
  var quick = document.querySelector(".quick_area");

  function setNav(open) {
    document.body.classList.toggle("nav-open", open);
    if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      setNav(!document.body.classList.contains("nav-open"));
    });
  }

  function placeQuick() {
    if (!quick) return;
    if (!wide.matches) {
      quick.style.top = "";
      return;
    }
    quick.style.top = "148px";
  }

  function onWidthChange() {
    if (wide.matches) setNav(false);
    placeQuick();
  }

  if (wide.addEventListener) wide.addEventListener("change", onWidthChange);
  else if (wide.addListener) wide.addListener(onWidthChange);
  placeQuick();

  if (familyBtn && familyMenu) {
    familyBtn.addEventListener("click", function () {
      var open = familyMenu.hasAttribute("hidden");
      if (open) familyMenu.removeAttribute("hidden");
      else familyMenu.setAttribute("hidden", "");
      familyBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  document.addEventListener("submit", function (event) {
    event.preventDefault();
  });

  document.addEventListener("click", function (event) {
    var link = event.target.closest ? event.target.closest("a") : null;
    if (!link) return;
    var href = link.getAttribute("href");
    if (href === "#" || href === "#none" || href === "") event.preventDefault();
  });

  window.callCategory = function () { return false; };
  window.callWrite = function () { return false; };
  window.callList = function () {
    window.location.href = "/cndh-clone/responsive/customer/noticeList.html";
    return false;
  };
})();
