(function () {
  const style = document.createElement("style");
  style.textContent = `
    #ruchi-chat-bubble {
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: #c0521f;
      color: #fff;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      box-shadow: 0 6px 20px rgba(192,82,31,0.4);
      z-index: 9998;
      transition: transform .2s ease, box-shadow .2s ease;
    }
    #ruchi-chat-bubble:hover {
      transform: scale(1.08);
      box-shadow: 0 8px 26px rgba(192,82,31,0.5);
    }
    #ruchi-chat-bubble .ping {
      position: absolute;
      top: -3px;
      right: -3px;
      width: 16px;
      height: 16px;
      background: #4c7256;
      border-radius: 50%;
      border: 2px solid #fff;
    }

    #ruchi-chat-window {
      position: fixed;
      bottom: 96px;
      right: 24px;
      width: 340px;
      max-width: calc(100vw - 48px);
      height: 460px;
      max-height: calc(100vh - 140px);
      background: #fff;
      border-radius: 18px;
      box-shadow: 0 16px 48px rgba(43,36,32,0.22);
      display: none;
      flex-direction: column;
      overflow: hidden;
      z-index: 9999;
      font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
      border: 1px solid #f0e6d8;
    }
    #ruchi-chat-window.open { display: flex; }

    #ruchi-chat-header {
      background: #2b2420;
      color: #fff;
      padding: 16px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }
    #ruchi-chat-header .title {
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 700;
      font-size: .95rem;
    }
    #ruchi-chat-header .title .dot {
      width: 8px; height: 8px; border-radius: 50%; background: #4c7256;
    }
    #ruchi-chat-header .sub {
      font-size: .72rem;
      color: #cfc6b8;
      font-weight: 500;
      margin-top: 2px;
    }
    #ruchi-chat-close {
      background: none;
      border: none;
      color: #cfc6b8;
      font-size: 20px;
      cursor: pointer;
      line-height: 1;
      padding: 4px;
    }
    #ruchi-chat-close:hover { color: #fff; }

    #ruchi-chat-body {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      background: #faf6ee;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .ruchi-msg {
      max-width: 82%;
      padding: 10px 14px;
      border-radius: 14px;
      font-size: .88rem;
      line-height: 1.4;
    }
    .ruchi-msg.bot {
      background: #fff;
      border: 1px solid #f0e6d8;
      color: #2b2420;
      align-self: flex-start;
      border-bottom-left-radius: 4px;
    }
    .ruchi-msg.user {
      background: #c0521f;
      color: #fff;
      align-self: flex-end;
      border-bottom-right-radius: 4px;
    }

    #ruchi-chat-input-row {
      display: flex;
      gap: 8px;
      padding: 12px;
      border-top: 1px solid #f0e6d8;
      background: #fff;
      flex-shrink: 0;
    }
    #ruchi-chat-input {
      flex: 1;
      border: 1px solid #f0e6d8;
      border-radius: 20px;
      padding: 10px 16px;
      font-size: .88rem;
      outline: none;
      font-family: inherit;
    }
    #ruchi-chat-input:focus { border-color: #c0521f; }
    #ruchi-chat-send {
      background: #c0521f;
      color: #fff;
      border: none;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      cursor: pointer;
      font-size: 16px;
      flex-shrink: 0;
    }
    #ruchi-chat-send:hover { background: #a5451a; }

    @media (max-width: 480px) {
      #ruchi-chat-window {
        left: 12px;
        right: 12px;
        width: auto;
        bottom: 86px;
      }
      #ruchi-chat-bubble { right: 16px; bottom: 16px; }
    }
  `;
  document.head.appendChild(style);

  const bubble = document.createElement("button");
  bubble.id = "ruchi-chat-bubble";
  bubble.setAttribute("aria-label", "Chat with Ruchi");
  bubble.innerHTML = `💬<span class="ping"></span>`;

  const win = document.createElement("div");
  win.id = "ruchi-chat-window";
  win.innerHTML = `
    <div id="ruchi-chat-header">
      <div>
        <div class="title"><span class="dot"></span>Ruchi Assistant</div>
        <div class="sub">Usually replies instantly</div>
      </div>
      <button id="ruchi-chat-close" aria-label="Close chat">✕</button>
    </div>
    <div id="ruchi-chat-body"></div>
    <div id="ruchi-chat-input-row">
      <input id="ruchi-chat-input" type="text" placeholder="Type a message…" autocomplete="off">
      <button id="ruchi-chat-send" aria-label="Send">➤</button>
    </div>
  `;

  document.body.appendChild(bubble);
  document.body.appendChild(win);

  const body = win.querySelector("#ruchi-chat-body");
  const input = win.querySelector("#ruchi-chat-input");

  // ===== Chat history persistence (survives page refresh) =====
  // Scoped per logged-in account (falls back to a shared "guest" bucket)
  // so switching accounts on the same browser never shows one customer's
  // chat — including their order details — to a different customer.
  localStorage.removeItem("ruchiChatHistory"); // drop the old unscoped key
  const STORAGE_KEY = `ruchiChatHistory:${localStorage.getItem("ruchiToken") || "guest"}`;

  function loadHistory() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch {
      return [];
    }
  }

  function saveHistory() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  }

  let history = loadHistory();

  function renderHistory() {
    body.innerHTML = "";
    history.forEach((m) => {
      const el = document.createElement("div");
      el.className = `ruchi-msg ${m.sender}`;
      el.textContent = m.text;
      body.appendChild(el);
    });
    body.scrollTop = body.scrollHeight;
  }

  function addMessage(text, sender, persist = true) {
    const el = document.createElement("div");
    el.className = `ruchi-msg ${sender}`;
    el.textContent = text;
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
    if (persist) {
      history.push({ text, sender });
      saveHistory();
    }
    return el;
  }

  // Updates a placeholder bubble (e.g. the "…" typing indicator) with its
  // final text and persists that final text — not the placeholder — to history.
  function finalizeMessage(el, text) {
    el.textContent = text;
    history.push({ text, sender: "bot" });
    saveHistory();
  }

  function botReply(text) {
    addMessage(text, "bot");
  }

  // ===== Backend URLs =====
  const CHAT_API = "http://127.0.0.1:8000/chat";
  const ORDERS_API = "http://127.0.0.1:5000/api/orders";

  let awaitingPhoneFor = null; // "track" | "items" | "spending"

  function startConversation() {
    body.innerHTML = "";
    history = [];
    saveHistory();
    botReply("Hi there! 👋 I'm the Ruchi assistant. Ask me anything — delivery time, restaurants, or say 'track my order', 'what did I order', or 'how much have I spent' to check your order.");
  }

  function askForPhone(intent) {
    awaitingPhoneFor = intent;
    botReply("Sure! Please type the phone number used for your order.");
  }

  function replyWithLatestOrder(orders, intent) {
    if (!orders || orders.length === 0) {
      botReply("I couldn't find any orders on your account yet. Visit the Restaurants page to place your first order.");
      return;
    }

    const latest = orders[0];
    const orderId = latest.id || latest.order_id || "—";

    if (intent === "items") {
      const items = latest.items || [];
      if (items.length === 0) {
        botReply(`📦 Order #${orderId} doesn't have item details on file.`);
      } else {
        const list = items
          .map((it) => `• ${it.name || "Item"} x${it.quantity || 1}`)
          .join("\n");
        botReply(`📦 Order #${orderId} — you ordered:\n${list}`);
      }
    } else {
      const statusText = latest.status || "Processing";
      botReply(`📦 Order #${orderId} — Status: ${statusText}`);
    }
  }

  // NEW: total amount spent across all of a customer's orders
  function replyWithSpending(orders) {
    if (!orders || orders.length === 0) {
      botReply("You haven't placed any orders yet — nothing spent so far!");
      return;
    }
    const totalSpent = orders
      .filter((o) => o.status !== "Cancelled")
      .reduce((sum, o) => sum + (o.total || 0), 0);
    botReply(`💰 You've placed ${orders.length} order(s) and spent a total of ₹${totalSpent} so far.`);
  }

  // Logged-in customers get their orders looked up by their account
  // (via the bearer token) — no need to ask for a phone number.
  async function lookupMyOrders(intent) {
    const token = localStorage.getItem("ruchiToken");
    if (!token) return false;
    botReply("Checking your order… ⏳");
    try {
      const res = await fetch(`${ORDERS_API}/me`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (!res.ok) return false; // token missing/expired — fall back to phone lookup
      const data = await res.json();
      const orders = Array.isArray(data) ? data : [];

      if (intent === "spending") {
        replyWithSpending(orders);
      } else {
        replyWithLatestOrder(orders, intent);
      }
      return true;
    } catch (err) {
      console.error("Order lookup error:", err);
      return false;
    }
  }

  async function lookupOrder(phone, intent) {
    botReply("Checking your order… ⏳");
    try {
      const res = await fetch(`${ORDERS_API}?phone=${encodeURIComponent(phone)}`);
      const data = await res.json();

      if (!res.ok || !data || (Array.isArray(data) && data.length === 0)) {
        botReply("I couldn't find any orders for that number. Double-check it, or visit the Restaurants page to place a new order.");
        return;
      }

      const orders = Array.isArray(data) ? data : [data];

      if (intent === "spending") {
        replyWithSpending(orders);
      } else {
        replyWithLatestOrder(orders, intent);
      }
    } catch (err) {
      console.error("Order lookup error:", err);
      botReply("Sorry, I couldn't reach the order system right now. Please check the Orders page directly.");
    }
  }

  async function askAI(text) {
    const typingEl = addMessage("…", "bot", false);
    try {
      const token = localStorage.getItem("ruchiToken");
      const res = await fetch(CHAT_API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, token })
      });
      const data = await res.json();
      finalizeMessage(typingEl, data.response || "Sorry, I didn't quite get that.");
    } catch (err) {
      console.error("Chatbot AI error:", err);
      finalizeMessage(typingEl, "I'm having trouble connecting right now. Please try again in a moment.");
    }
  }

  function handleUserText(text) {
    const t = text.toLowerCase();

    // If we previously asked for a phone number, treat this message as the phone
    if (awaitingPhoneFor) {
      const intent = awaitingPhoneFor;
      awaitingPhoneFor = null;
      lookupOrder(text.trim(), intent);
      return;
    }

    // "how much have I spent" / "total amount" / "amt spent" — spending intent
    if (/how much.*(spent|spend)|amt.*spent|amount.*spent|total.*(spent|spend|paid)|how many amt/.test(t)) {
      resolveOrderIntent("spending");
    // Explicit order-status/tracking intent
    } else if (/track my order|order status|where is my order|track order/.test(t)) {
      resolveOrderIntent("track");
    // Any other first-person question about their order's contents — "what did
    // I order", "what dishes/items/flavour do I have", typos and rephrasings
    // included. Broad on purpose: a fixed phrase list keeps missing real
    // questions (e.g. "flavour" instead of "items").
    } else if (/\b(order|dish|item|flavou?r|food|meal|ate|eat|bought)\w*\b/.test(t) && /\b(i|my|me|mine)\b/.test(t)) {
      if (localStorage.getItem("ruchiToken")) {
        // Logged in — the AI already gets this customer's full order + item
        // history via the token, and can reason across all their orders
        // (not just the latest one), so let it answer directly.
        askAI(text);
      } else {
        // Guest — the AI has no way to know who they are, so fall back to
        // the phone-number lookup flow instead of a generic "no data" reply.
        resolveOrderIntent("items");
      }
    } else {
      askAI(text); // everything else (including "delivery time") goes to the AI
    }
  }

  // Logged-in customers get looked up by account automatically;
  // only ask for a phone number as a guest fallback.
  async function resolveOrderIntent(intent) {
    if (localStorage.getItem("ruchiToken")) {
      const found = await lookupMyOrders(intent);
      if (found) return;
    }
    askForPhone(intent);
  }

  bubble.addEventListener("click", () => {
    win.classList.add("open");
    bubble.style.display = "none";
    if (body.children.length === 0) {
      if (history.length > 0) {
        renderHistory();
      } else {
        startConversation();
      }
    }
  });

  win.querySelector("#ruchi-chat-close").addEventListener("click", () => {
    win.classList.remove("open");
    bubble.style.display = "flex";
  });

  function sendUserMessage() {
    const text = input.value.trim();
    if (!text) return;
    addMessage(text, "user");
    input.value = "";
    setTimeout(() => handleUserText(text), 350);
  }

  win.querySelector("#ruchi-chat-send").addEventListener("click", sendUserMessage);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendUserMessage();
  });
})();