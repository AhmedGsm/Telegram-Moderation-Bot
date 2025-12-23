/**
bot.js

Client-side helper for triggering bot execution from the UI.
Provides a safe POST wrapper and minimal user feedback handling.
*/


    async function safeFetch(url, payload) {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload || {})
      });
      return res.json();
    }

    function showMessage(message, type = 'success') {
      const box = document.getElementById('messageBox');
      box.textContent = message;
      box.className = `message-box ${type}`;
      box.style.display = 'block';
    }

    document.getElementById('runBotBtn').addEventListener('click', async () => {
      try {
        const data = await safeFetch('/run_bot', {});
        if (data.status === 'success') {
          showMessage(data.message, 'success');
        } else {
          showMessage(data.message || 'Failed to start bot.', 'error');
        }
      } catch (e) {
        showMessage('Error: ' + e.message, 'error');
      }
    });