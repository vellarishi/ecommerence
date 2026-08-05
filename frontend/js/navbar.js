function updateNavbar() {
  const token = localStorage.getItem('ruchiToken');
  const loginBtn = document.querySelector('a[href="login.html"]');

  if (!loginBtn) return; 

  if (token) {
    loginBtn.textContent = 'Logout';
    loginBtn.removeAttribute('href');
    loginBtn.style.cursor = 'pointer';
    loginBtn.onclick = function () {
      localStorage.removeItem('ruchiToken');
      localStorage.removeItem('ruchiCustomer');
      localStorage.removeItem('ruchiPhone');
      window.location.href = 'login.html';
    };
  } else {
    loginBtn.textContent = 'Login';
    loginBtn.setAttribute('href', 'login.html');
    loginBtn.onclick = null;
  }
}

function setupMobileNav() {
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (!toggle || !links) return;

  toggle.addEventListener('click', function () {
    links.classList.toggle('open');
  });

  links.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      links.classList.remove('open');
    });
  });
}

document.addEventListener('DOMContentLoaded', updateNavbar);
document.addEventListener('DOMContentLoaded', setupMobileNav);