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

document.addEventListener('DOMContentLoaded', updateNavbar);