const BASE_URL = window.location.origin;

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

function getPreferredTheme() {
  const stored = localStorage.getItem('theme');
  if (stored) return stored;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function setTheme(theme) {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  localStorage.setItem('theme', theme);
  themeToggle.textContent = theme === 'dark' ? '🌙' : '☀️';
}

setTheme(getPreferredTheme());

themeToggle.addEventListener('click', () => {
  const isDark = document.documentElement.classList.contains('dark');
  setTheme(isDark ? 'light' : 'dark');
});

function showToast(message, type = 'success') {
  clearTimeout(toastTimer);

  toast.textContent = message;
  toast.className =
    'fixed bottom-5 right-5 px-4 py-3 rounded-xl shadow-lg transition-all duration-300 text-sm font-medium z-50 transform translate-y-0 opacity-100 pointer-events-auto flex items-center gap-2';

  if (type === 'error') {
    toast.classList.add('bg-red-600', 'text-white');
  } else {
    toast.classList.add(
      'bg-gray-900',
      'text-white',
      'dark:bg-gray-100',
      'dark:text-gray-900',
    );
  }

  toastTimer = setTimeout(() => {
    toast.classList.remove('opacity-100', 'translate-y-0', 'pointer-events-auto');
    toast.classList.add('opacity-0', 'translate-y-2', 'pointer-events-none');
  }, 3000);
}

copyBtn.addEventListener('click', async () => {
  const url = resultLink.href;
  try {
    await navigator.clipboard.writeText(url);
    copyBtn.textContent = 'Copied!';
    copyBtn.classList.add('bg-green-600', 'text-white', 'dark:bg-green-600');

    setTimeout(() => {
      copyBtn.textContent = 'Copy';
      copyBtn.classList.remove('bg-green-600', 'text-white', 'dark:bg-green-600');
    }, 2000);
  } catch {
    showToast('Failed to copy', 'error');
  }
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const url = urlInput.value.trim();
  if (!url) return;

  submitBtn.disabled = true;
  submitBtn.classList.add('opacity-75', 'cursor-not-allowed');
  btnText.classList.add('hidden');
  btnSpinner.classList.remove('hidden');
  resultCard.classList.add('hidden');

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

    const shortUrl = `${BASE_URL}/${data.short_id}`;
    resultLink.href = shortUrl;
    resultLink.textContent = shortUrl;
    resultCard.classList.remove('hidden');

    showToast('Link created! 🎉');

    loadHistory();
  } catch (err) {
    showToast('Failed to connect to server', 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.classList.remove('opacity-75', 'cursor-not-allowed');
    btnText.classList.remove('hidden');
    btnSpinner.classList.add('hidden');
  }
});

async function loadHistory() {
  try {
    const res = await fetch(`${BASE_URL}/urls`);
    const urls = await res.json();

    if (!urls.length) {
      historyList.innerHTML = `
        <div class="text-center py-6 text-gray-500 dark:text-gray-400 text-sm">
          No shortened links yet
        </div>`;
      return;
    }

    historyList.innerHTML = urls
      .map((u) => {
        const shortUrl = `${BASE_URL}/${u.short_id}`;
        return `
            <div class="flex items-center justify-between p-3.5 bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition">
              <div class="min-w-0 flex-1 mr-4">
                <a href="${shortUrl}" target="_blank" rel="noopener" class="text-blue-600 dark:text-blue-400 font-medium hover:underline block truncate">
                  /${u.short_id}
                </a>
                <div class="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5" title="${u.target_url}">
                  ${u.target_url}
                </div>
              </div>
              <div class="flex items-center space-x-1 text-xs font-medium text-gray-500 dark:text-gray-400 bg-gray-200/60 dark:bg-gray-800 px-2.5 py-1 rounded-lg shrink-0">
                <span>👁</span>
                <span>${u.clicks}</span>
              </div>
            </div>
          `;
      })
      .join('');
  } catch {}
}

loadHistory();
