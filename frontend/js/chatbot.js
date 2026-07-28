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

  function addMessage(text, sender) {
    const el = document.createElement("div");
    el.className = `ruchi-msg ${sender}`;
    el.textContent = text;
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
    return el;
  }

  function botReply(text) {
    addMessage(text, "bot");
  }

  // ===== Backend URLs =====
  const CHAT_API = "https://ecommerence-3lrk.onrender.com/chat";
  const ORDERS_API = "https://ecommerence-3lrk.onrender.com/api/orders";

  let awaitingPhoneFor = null; // "track" | "items"

  function startConversation() {
    body.innerHTML = "";
    botReply("Hi there! 👋 I'm the Ruchi assistant. Ask me anything — delivery time, restaurants, or say 'track my order' or 'what did I order' to check your order.");
  }

  function askForPhone(intent) {
    awaitingPhoneFor = intent;
    botReply("Sure! Please type the phone number used for your order.");
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
    } catch (err) {
      console.error("Order lookup error:", err);
      botReply("Sorry, I couldn't reach the order system right now. Please check the Orders page directly.");
    }
  }

  async function askAI(text) {
    const typingEl = addMessage("…", "bot");
    try {
      const res = await fetch(CHAT_API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      typingEl.textContent = data.response || "Sorry, I didn't quite get that.";
    } catch (err) {
      console.error("Chatbot AI error:", err);
      typingEl.textContent = "I'm having trouble connecting right now. Please try again in a moment.";
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

    // "what did I order" / "what items did I order" etc. — show the order's items
    if (/what.*(items|did i order|i ordered)|order items|items i ordered/.test(t)) {
      askForPhone("items");
    // Explicit order-status/tracking intent
    } else if (/track my order|order status|where is my order|track order/.test(t)) {
      askForPhone("track");
    } else {
      askAI(text); // everything else (including "delivery time") goes to the AI
    }
  }

  bubble.addEventListener("click", () => {
    win.classList.add("open");
    bubble.style.display = "none";
    if (body.children.length === 0) startConversation();
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