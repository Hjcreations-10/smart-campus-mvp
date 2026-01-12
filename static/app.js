async function checkAccess() {
  const urlInput = document.getElementById("url").value.trim();
  const resultBox = document.getElementById("result");

  if (!urlInput) {
    resultBox.innerText = "⚠️ Please enter a website URL.";
    resultBox.style.color = "orange";
    return;
  }

  try {
    const response = await fetch("/check_url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: urlInput })
    });

    const data = await response.json();

    if (data.status === "ALLOWED") {
      resultBox.innerText = "✅ Access Granted: Educational site";
      resultBox.style.color = "green";
    } else if (data.status === "BLOCKED") {
      resultBox.innerText = "❌ Access Blocked: Non-educational site";
      resultBox.style.color = "red";
    } else if (data.status === "ERROR") {
      resultBox.innerText = "⚠️ Server error: " + data.error;
      resultBox.style.color = "orange";
    } else {
      resultBox.innerText = "⚠️ Unexpected response from server.";
      resultBox.style.color = "gray";
    }
  } catch (error) {
    resultBox.innerText = "❌ Error connecting to server: " + error;
    resultBox.style.color = "red";
  }
}

