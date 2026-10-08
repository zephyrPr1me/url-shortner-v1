const BASE_URL = window.location.origin;

// DOM refs
const form = document.getElementById('shortenForm');
const urlInput = document.getElementById('urlInput');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');
const btnSpinner = document.getElementById('btnSpinner');
const resultCard = document.getElementById('resultCard');
const resultLink = document.getElementById('resultLink');
const copyBtn = document.getElementById('copyBtn');
const historyList = document.getElementById('historyList');
const toast = document.getElementById('toast');
const themeToggle = document.getElementById('themeToggle');

let toastTimer = null;

// ── Theme ──
function getPreferredTheme() {
  const stored = localStorage.getItem('theme');
  if (stored) return stored;
  return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
}

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  themeToggle.textContent = theme === 'dark' ? '🌙' : '☀️';
}

setTheme(getPreferredTheme());

themeToggle.addEventListener('click', () => {
  const current = document.documentElement.getAttribute('data-theme');
  setTheme(current === 'dark' ? 'light' : 'dark');
});

// ── Toast ──
function showToast(message, type = 'success') {
  clearTimeout(toastTimer);
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toast.classList.add('visible');
  toastTimer = setTimeout(() => toast.classList.remove('visible'), 3000);
}

// ── Copy ──
copyBtn.addEventListener('click', async () => {
  const url = resultLink.href;
  try {
    await navigator.clipboard.writeText(url);
    copyBtn.textContent = 'Copied!';
    copyBtn.classList.add('copied');
    setTimeout(() => {
      copyBtn.textContent = 'Copy';
      copyBtn.classList.remove('copied');
    }, 2000);
  } catch {
    showToast('Failed to copy', 'error');
  }
});

// ── Shorten ──
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const url = urlInput.value.trim();
  if (!url) return;

  // Loading state
  submitBtn.disabled = true;
  btnText.style.display = 'none';
  btnSpinner.style.display = 'inline-block';
  resultCard.classList.remove('visible');

  try {
    const res = await fetch(`${BASE_URL}/shorten`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_url: url }),
    });

    const data = await res.json();

    if (!res.ok) {
      showToast(data.detail || 'Server error', 'error');
      return;
    }

    // Show result
    const shortUrl = `${BASE_URL}/${data.short_id}`;
    resultLink.href = shortUrl;
    resultLink.textContent = shortUrl;
    resultCard.classList.add('visible');

    showToast('Link created! 🎉');

    // Refresh history
    loadHistory();
  } catch (err) {
    showToast('Failed to connect to server', 'error');
  } finally {
    submitBtn.disabled = false;
    btnText.style.display = 'inline';
    btnSpinner.style.display = 'none';
  }
});

// ── History ──
async function loadHistory() {
  try {
    const res = await fetch(`${BASE_URL}/urls`);
    const urls = await res.json();

    if (!urls.length) {
      historyList.innerHTML = `<div class="history-empty">No shortened links yet</div>`;
      return;
    }

    historyList.innerHTML = urls
      .map((u) => {
        const shortUrl = `${BASE_URL}/${u.short_id}`;
        const date = new Date(u.created_at).toLocaleDateString('ru-RU', {
          day: 'numeric',
          month: 'short',
          hour: '2-digit',
          minute: '2-digit',
        });
        return `
            <div class="history-item">
              <div class="short-link">
                <a href="${shortUrl}" target="_blank" rel="noopener">/${u.short_id}</a>
                <div class="original-link" title="${u.target_url}">${u.target_url}</div>
              </div>
              <div class="clicks">👁 <span>${u.clicks}</span></div>
            </div>
          `;
      })
      .join('');
  } catch {
    // silently fail
  }
}

// Load history on page load
loadHistory();
