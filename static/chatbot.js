async function liveSuggestions() {
  const input = document.getElementById("userInput").value.toLowerCase();
  const suggestionBox = document.getElementById("suggestions");

  if (input.length === 0) {
    suggestionBox.style.display = "none";
    return;
  }

  const res = await fetch(`/suggest?q=${encodeURIComponent(input)}`, {
    method: "GET",
    credentials: "include", // Important!
    headers: { "Content-Type": "application/json" },
  });

  const data = await res.json();

  suggestionBox.innerHTML = "";
  if (data.length > 0) {
    data.forEach((item) => {
      const div = document.createElement("div");
      div.className = "suggestion-item";
      div.textContent = item.title;
      div.onclick = () => {
        document.getElementById("userInput").value = item.title;
        suggestionBox.style.display = "none";
        handleUserInput(); // Trigger search
      };
      suggestionBox.appendChild(div);
    });
    suggestionBox.style.display = "block";
  } else {
    // Show "No matches found." in the suggestion box
    const div = document.createElement("div");
    div.className = "suggestion-item";
    div.style.color = "#888";
    div.style.cursor = "default";
    div.textContent = "No matches found.";
    suggestionBox.appendChild(div);
    suggestionBox.style.display = "block";
  }
}

function keyDownHandler(e) {
  if (e.key === "Enter") {
    handleUserInput();
    document.getElementById("suggestions").style.display = "none";
  }
}

async function handleUserInput() {
  document.getElementById("suggestions").style.display = "none";
  const input = document.getElementById("userInput").value;
  if (!input) return;

  const chatLog = document.getElementById("chatLog");

  // User message (right side)
  const userBubble = document.createElement("div");
  userBubble.className = "bubble user";
  userBubble.innerHTML = `<b>You:</b> ${input}`;
  chatLog.appendChild(userBubble);
  chatLog.scrollTop = chatLog.scrollHeight;

  // Bot thinking indicator
  const thinking = document.createElement("div");
  thinking.className = "bubble bot";
  thinking.innerHTML = `
    <div class="thinking-indicator">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>`;
  chatLog.appendChild(thinking);
  chatLog.scrollTop = chatLog.scrollHeight;

  document.getElementById("userInput").value = "";
  document.getElementById("userInput").focus();

  // Start both the fetch and the delay at the same time
  const fetchPromise = fetch(`/suggest?q=${encodeURIComponent(input)}`).then(
    (res) => res.json()
  );
  const delayPromise = new Promise((res) => setTimeout(res, 600));
  const [data] = await Promise.all([fetchPromise, delayPromise]);

  // Remove thinking indicator
  chatLog.removeChild(thinking);

  // Bot response (left side)
  if (data.length) {
    for (const item of data) {
      await new Promise((res) => setTimeout(res, 120)); // smooth delay between each menu
      const botBubble = document.createElement("div");
      botBubble.className = "bubble bot";
      botBubble.innerHTML = `
        <b>${item.title}</b><br>
        <span>${
          item.description
            ? item.description.replace(/\.? ?Follow Link:.*$/, ".")
            : ""
        }</span><br>
        <a href="${
          item.url
        }" target="_blank" class="follow-link-btn">Follow Link</a>
      `;
      chatLog.appendChild(botBubble);
      chatLog.scrollTop = chatLog.scrollHeight;
    }
  } else {
    const botBubble = document.createElement("div");
    botBubble.className = "bubble bot";
    botBubble.textContent = "No matching menus found.";
    chatLog.appendChild(botBubble);
    chatLog.scrollTop = chatLog.scrollHeight;
  }
}

function startNewChat() {
  const chatLog = document.getElementById("chatLog");
  chatLog.innerHTML = `<div class="bubble bot"><b>🤖</b> How can I help you?</div>`;
}
