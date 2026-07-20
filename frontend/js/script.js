/* ==========================================================================
   script.js
   Covers: 1) Login/Register validation  2) Restaurants data + display
           3) Nav toggle / cart / filters  4) Dummy data (easy to swap to API)

   IMPORTANT: Element IDs/classes below are ASSUMPTIONS based on common
   naming. Open your actual HTML files and match these IDs, OR rename
   the IDs in your HTML to match these — whichever is faster for you.
   ========================================================================== */


/* ==========================================================================
   SECTION 0: DUMMY DATA
   Later, replace this array with a fetch() call to your real backend.
   Keeping it in one place means only ONE function needs to change later.
   ========================================================================== */

const restaurantsData = [
  {
    id: 1,
    name: "Spice Garden",
    cuisine: "South Indian",
    rating: 4.5,
    price: "₹₹",
    priceValue: 250, // numeric price used for cart/order totals
    image: "https://via.placeholder.com/300x200?text=Spice+Garden",
    deliveryTime: "30-40 min"
  },
  {
    id: 2,
    name: "Pizza Point",
    cuisine: "Italian",
    rating: 4.2,
    price: "₹₹₹",
    priceValue: 450,
    image: "https://via.placeholder.com/300x200?text=Pizza+Point",
    deliveryTime: "25-35 min"
  },
  {
    id: 3,
    name: "Dragon Wok",
    cuisine: "Chinese",
    rating: 4.0,
    price: "₹₹",
    priceValue: 300,
    image: "https://via.placeholder.com/300x200?text=Dragon+Wok",
    deliveryTime: "35-45 min"
  },
  {
    id: 4,
    name: "Burger Bay",
    cuisine: "Fast Food",
    rating: 4.3,
    price: "₹",
    priceValue: 150,
    image: "https://via.placeholder.com/300x200?text=Burger+Bay",
    deliveryTime: "20-30 min"
  }
];


/* ==========================================================================
   SECTION 1: LOGIN & REGISTER FORM VALIDATION
   ==========================================================================
   Expected HTML (adjust IDs in your HTML to match, or vice versa):

   Login form:
     <form id="loginForm">
       <input id="loginEmail" type="email">
       <input id="loginPassword" type="password">
       <span id="loginError"></span>
     </form>

   Register form:
     <form id="registerForm">
       <input id="registerName" type="text">
       <input id="registerEmail" type="email">
       <input id="registerPassword" type="password">
       <input id="registerConfirmPassword" type="password">
       <span id="registerError"></span>
     </form>
   ========================================================================== */

// --- Reusable validators (why: avoids repeating regex logic in both forms) ---
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function isStrongPassword(password) {
  // At least 6 characters — adjust rule as needed
  return password.length >= 6;
}

function showError(elementId, message) {
  const errorEl = document.getElementById(elementId);
  if (errorEl) {
    errorEl.textContent = message;
    errorEl.style.color = "red";
  }
}

function clearError(elementId) {
  const errorEl = document.getElementById(elementId);
  if (errorEl) errorEl.textContent = "";
}

// --- LOGIN handling ---
const loginForm = document.getElementById("loginForm");

if (loginForm) {
  loginForm.addEventListener("submit", function (e) {
    e.preventDefault(); // stop page reload, we handle it manually
    clearError("loginError");

    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();

    if (!email || !password) {
      showError("loginError", "Please fill in all fields.");
      return;
    }

    if (!isValidEmail(email)) {
      showError("loginError", "Please enter a valid email address.");
      return;
    }

    // ---- Replace this block with a real API call later ----
    // Example:
    // fetch("/api/login", { method: "POST", body: JSON.stringify({email, password}) })
    console.log("Login submitted:", { email, password });
    alert("Login successful! (dummy check — connect backend for real auth)");
    // window.location.href = "restaurants.html"; // redirect after real login
  });
}

// --- REGISTER handling ---
const registerForm = document.getElementById("registerForm");

if (registerForm) {
  registerForm.addEventListener("submit", function (e) {
    e.preventDefault();
    clearError("registerError");

    const name = document.getElementById("registerName").value.trim();
    const email = document.getElementById("registerEmail").value.trim();
    const password = document.getElementById("registerPassword").value.trim();
    const confirmPassword = document
      .getElementById("registerConfirmPassword")
      .value.trim();

    if (!name || !email || !password || !confirmPassword) {
      showError("registerError", "Please fill in all fields.");
      return;
    }

    if (!isValidEmail(email)) {
      showError("registerError", "Please enter a valid email address.");
      return;
    }

    if (!isStrongPassword(password)) {
      showError("registerError", "Password must be at least 6 characters.");
      return;
    }

    if (password !== confirmPassword) {
      showError("registerError", "Passwords do not match.");
      return;
    }

    // ---- Replace this block with a real API call later ----
    console.log("Register submitted:", { name, email, password });
    alert("Registration successful! (dummy check — connect backend for real signup)");
    // window.location.href = "login.html";
  });
}


/* ==========================================================================
   SECTION 2: RESTAURANTS PAGE — FETCH/DISPLAY DATA
   ==========================================================================
   Expected HTML:
     <div id="restaurantList"></div>
     <input id="searchInput" type="text">
     <select id="cuisineFilter">
       <option value="all">All</option>
       <option value="South Indian">South Indian</option>
       ...
     </select>
   ========================================================================== */

function renderRestaurants(list) {
  const container = document.getElementById("restaurantList");
  if (!container) return; // this section only runs on restaurants.html

  if (list.length === 0) {
    container.innerHTML = `<p>No restaurants found.</p>`;
    return;
  }

  // Build all cards as one HTML string — faster than multiple DOM inserts
  container.innerHTML = list
    .map(
      (r) => `
      <div class="restaurant-card" data-id="${r.id}">
        <img src="${r.image}" alt="${r.name}">
        <h3>${r.name}</h3>
        <p>${r.cuisine} • ${r.price}</p>
        <p>⭐ ${r.rating} • ${r.deliveryTime}</p>
        <button class="view-btn" data-id="${r.id}">View Menu</button>
      </div>
    `
    )
    .join("");

  attachCardListeners();
}

function attachCardListeners() {
  document.querySelectorAll(".view-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      const id = this.getAttribute("data-id");
      console.log("Clicked restaurant id:", id);
      // window.location.href = `menu.html?id=${id}`; // if you add a menu page
    });
  });
}

// ---- Later, replace this with real fetch ----
// async function loadRestaurants() {
//   const res = await fetch("/api/restaurants");
//   const data = await res.json();
//   renderRestaurants(data);
// }
function loadRestaurants() {
  renderRestaurants(restaurantsData); // using dummy data for now
}

// Run only if we're on restaurants page (container exists)
if (document.getElementById("restaurantList")) {
  loadRestaurants();
}

// --- Search filter ---
const searchInput = document.getElementById("searchInput");
if (searchInput) {
  searchInput.addEventListener("input", function () {
    const query = this.value.toLowerCase();
    const filtered = restaurantsData.filter((r) =>
      r.name.toLowerCase().includes(query)
    );
    renderRestaurants(filtered);
  });
}

// --- Cuisine filter ---
const cuisineFilter = document.getElementById("cuisineFilter");
if (cuisineFilter) {
  cuisineFilter.addEventListener("change", function () {
    const value = this.value;
    const filtered =
      value === "all"
        ? restaurantsData
        : restaurantsData.filter((r) => r.cuisine === value);
    renderRestaurants(filtered);
  });
}


/* ==========================================================================
   SECTION 3: NAVIGATION TOGGLE + CART
   ==========================================================================
   Expected HTML:
     <button id="menuToggle"></button>
     <nav id="navMenu"></nav>

     <button class="add-to-cart" data-id="1"></button>
     <span id="cartCount">0</span>
   ========================================================================== */

// --- Mobile nav toggle ---
const menuToggle = document.getElementById("menuToggle");
const navMenu = document.getElementById("navMenu");

if (menuToggle && navMenu) {
  menuToggle.addEventListener("click", function () {
    navMenu.classList.toggle("active"); // toggle a CSS class that shows/hides menu
  });
}

// --- Cart logic (persisted in localStorage so it survives page reloads/navigation) ---
function getCart() {
  return JSON.parse(localStorage.getItem("cart")) || [];
}

function saveCart(cart) {
  localStorage.setItem("cart", JSON.stringify(cart));
}

function updateCartCount() {
  const cartCountEl = document.getElementById("cartCount");
  if (cartCountEl) {
    cartCountEl.textContent = getCart().length;
  }
}

document.querySelectorAll(".add-to-cart").forEach((btn) => {
  btn.addEventListener("click", function () {
    const id = this.getAttribute("data-id");
    const item = restaurantsData.find((r) => r.id == id);
    if (!item) return;

    const cart = getCart();
    cart.push(item);
    saveCart(cart);
    updateCartCount();
    console.log("Cart:", cart);
  });
});

// --- Cart page rendering (only runs on cart.html) ---
function renderCart() {
  const container = document.getElementById("cartList");
  if (!container) return; // only runs on cart.html

  const cart = getCart();

  if (cart.length === 0) {
    container.innerHTML = `<p>Your cart is empty. Go add something from <a href="restaurants.html">restaurants</a>!</p>`;
    updateCartTotal();
    return;
  }

  container.innerHTML = cart
    .map(
      (item, index) => `
      <div class="order-card">
        <div class="order-header">
          <h3>${item.name}</h3>
          <button class="btn-ghost remove-item" data-index="${index}">Remove</button>
        </div>
        <p class="order-date">${item.cuisine || ""} • ${item.deliveryTime || ""}</p>
        <p class="order-total">₹${item.priceValue || 0}</p>
      </div>
    `
    )
    .join("");

  updateCartTotal();
  attachRemoveListeners();
}

function attachRemoveListeners() {
  document.querySelectorAll(".remove-item").forEach((btn) => {
    btn.addEventListener("click", function () {
      const index = parseInt(this.getAttribute("data-index"));
      const cart = getCart();
      cart.splice(index, 1); // remove that one item
      saveCart(cart);
      updateCartCount();
      renderCart();
    });
  });
}

function updateCartTotal() {
  const totalEl = document.getElementById("cartTotal");
  if (!totalEl) return;
  const cart = getCart();
  const total = cart.reduce((sum, item) => sum + (item.priceValue || 0), 0);
  totalEl.textContent = total;
}

if (document.getElementById("cartList")) {
  renderCart();
}

// --- Checkout: converts current cart into a saved order ---
function placeOrder() {
  const cart = getCart();
  if (cart.length === 0) {
    alert("Your cart is empty. Add something first!");
    return;
  }

  const orders = JSON.parse(localStorage.getItem("orders")) || [];

  const newOrder = {
    id: Date.now(), // unique id based on timestamp
    date: new Date().toLocaleDateString(),
    items: cart,
    total: cart.reduce((sum, item) => sum + (item.priceValue || 0), 0),
    status: "Placed"
  };

  orders.unshift(newOrder); // newest order first
  localStorage.setItem("orders", JSON.stringify(orders));

  saveCart([]); // clear cart after placing order
  updateCartCount();

  alert("Order placed successfully!");
  window.location.href = "orders.html"; // take user to their new order
}

const checkoutBtn = document.getElementById("checkoutBtn");
if (checkoutBtn) {
  checkoutBtn.addEventListener("click", placeOrder);
}

updateCartCount(); // run once on page load


/* ==========================================================================
   SECTION 4: CONTACT FORM
   ==========================================================================
   Expected HTML:
     <form id="contactForm">
       <input id="contactName">
       <input id="contactEmail">
       <textarea id="contactMessage"></textarea>
       <span id="contactStatus"></span>
     </form>
   ========================================================================== */

const contactForm = document.getElementById("contactForm");

if (contactForm) {
  contactForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const name = document.getElementById("contactName").value.trim();
    const email = document.getElementById("contactEmail").value.trim();
    const message = document.getElementById("contactMessage").value.trim();
    const statusEl = document.getElementById("contactStatus");

    if (!name || !email || !message) {
      statusEl.textContent = "Please fill in all fields.";
      statusEl.style.color = "red";
      return;
    }

    if (!isValidEmail(email)) {
      statusEl.textContent = "Please enter a valid email.";
      statusEl.style.color = "red";
      return;
    }

    // ---- Replace with real API call later ----
    console.log("Contact form submitted:", { name, email, message });
    statusEl.textContent = "Message sent! We'll get back to you soon.";
    statusEl.style.color = "green";
    contactForm.reset();
  });
}


/* ==========================================================================
   SECTION 5: ORDERS PAGE — DISPLAY ORDER HISTORY
   ==========================================================================
   Expected HTML:
     <div id="ordersList"></div>

   Reads real orders from localStorage (created by placeOrder() in Section 3).
   If none exist yet, shows dummy sample orders so the page isn't empty
   during development/testing.
   ========================================================================== */

// Dummy sample orders — shown ONLY if no real orders exist yet
const dummyOrders = [
  {
    id: 1001,
    date: "01/07/2026",
    customer: "Arun Kumar",
    items: [
      { name: "Spice Garden - Masala Dosa", priceValue: 120 },
      { name: "Spice Garden - Filter Coffee", priceValue: 40 }
    ],
    total: 160,
    status: "Delivered"
  },
  {
    id: 1002,
    date: "03/07/2026",
    customer: "Priya Sharma",
    items: [{ name: "Pizza Point - Margherita Pizza", priceValue: 349 }],
    total: 349,
    status: "Delivered"
  },
  {
    id: 1003,
    date: "04/07/2026",
    customer: "Ravi Shankar",
    items: [
      { name: "Dragon Wok - Veg Fried Rice", priceValue: 180 },
      { name: "Dragon Wok - Manchurian", priceValue: 150 }
    ],
    total: 330,
    status: "Delivered"
  },
  {
    id: 1004,
    date: "05/07/2026",
    customer: "Divya Prakash",
    items: [{ name: "Burger Bay - Cheese Burger Combo", priceValue: 220 }],
    total: 220,
    status: "Cancelled"
  },
  {
    id: 1005,
    date: "07/07/2026",
    customer: "Karthik Raja",
    items: [
      { name: "Spice Garden - Chicken Biryani", priceValue: 250 },
      { name: "Spice Garden - Raita", priceValue: 30 }
    ],
    total: 280,
    status: "Delivered"
  },
  {
    id: 1006,
    date: "08/07/2026",
    customer: "Meena Iyer",
    items: [{ name: "Pizza Point - Farmhouse Pizza", priceValue: 399 }],
    total: 399,
    status: "Delivered"
  },
  {
    id: 1007,
    date: "10/07/2026",
    customer: "Suresh Babu",
    items: [
      { name: "Dragon Wok - Noodles", priceValue: 170 },
      { name: "Dragon Wok - Spring Rolls", priceValue: 140 }
    ],
    total: 310,
    status: "Out for Delivery"
  },
  {
    id: 1008,
    date: "11/07/2026",
    customer: "Anitha Rajan",
    items: [{ name: "Burger Bay - Double Patty Burger", priceValue: 190 }],
    total: 190,
    status: "Preparing"
  },
  {
    id: 1009,
    date: "12/07/2026",
    customer: "Vignesh Muthu",
    items: [
      { name: "Spice Garden - Idli Sambar", priceValue: 80 },
      { name: "Spice Garden - Vada", priceValue: 50 }
    ],
    total: 130,
    status: "Placed"
  },
  {
    id: 1010,
    date: "13/07/2026",
    customer: "Lakshmi Narayan",
    items: [{ name: "Pizza Point - Pepperoni Pizza", priceValue: 429 }],
    total: 429,
    status: "Placed"
  }
];

function renderOrders(orders) {
  const container = document.getElementById("ordersList");
  if (!container) return; // only runs on orders.html

  if (orders.length === 0) {
    container.innerHTML = `<p>No orders yet. Start browsing <a href="restaurants.html">restaurants</a>!</p>`;
    return;
  }

  container.innerHTML = orders
    .map(
      (order) => `
      <div class="order-card">
        <div class="order-header">
          <h3>Order #${order.id}${order.customer ? " — " + order.customer : ""}</h3>
          <span class="order-status ${order.status.toLowerCase().replace(/\s+/g, "-")}">${order.status}</span>
        </div>
        <p class="order-date">Placed on: ${order.date}</p>
        <ul class="order-items">
          ${order.items
            .map((item) => `<li>${item.name} — ₹${item.priceValue}</li>`)
            .join("")}
        </ul>
        <p class="order-total"><strong>Total: ₹${order.total}</strong></p>
      </div>
    `
    )
    .join("");
}

function loadOrders() {
  const savedOrders = JSON.parse(localStorage.getItem("orders")) || [];
  // If user has real orders, show those. Otherwise show dummy samples.
  const ordersToShow = savedOrders.length > 0 ? savedOrders : dummyOrders;
  renderOrders(ordersToShow);
}

if (document.getElementById("ordersList")) {
  loadOrders();
}