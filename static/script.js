document.addEventListener('DOMContentLoaded', function() {

  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.overlay');

  const registerBtn = document.getElementById('registerBtn');
  const listGroupsBtn = document.getElementById('listGroupsBtn');
  const verifyCodeBtn = document.getElementById('verifyCodeBtn');
  const verifyPasswordBtn = document.getElementById('verifyPasswordBtn');
  const messageBox = document.getElementById('messageBox');
  const groupsContainer = document.getElementById('groupsContainer');
  const passwordVerification = document.getElementById('passwordVerification');
  const listForm = document.getElementById('listIdsForm');
  const h1Title = document.querySelector('.form-container h1');
  const registerForm = document.getElementById('registerForm');
  const runBotButton = document.getElementById('runBotBtnContainer');
  const runBotBtn = document.getElementById('runBotBtn');

  // --- Helpers ---

  function showMessage(message, type = 'success') {
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`;
    messageBox.style.display = 'block';            // ensure visible now
    clearTimeout(showMessage._t);
    showMessage._t = setTimeout(() => {
      messageBox.style.display = 'none';
    }, 8000);
  }

  function setFormEnabled(formEl, enabled) {
    [...formEl.querySelectorAll('input, button')].forEach(el => {
      el.disabled = !enabled;
    });
  }

  async function safeFetch(url, payload) {
    const headers = { 'Content-Type': 'application/json' };
    // Optional CSRF header
    // const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
    // if (csrf) headers['X-CSRF-Token'] = csrf;

    const res = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload || {})
    });
    let json;
    try { json = await res.json(); } catch {
      throw new Error('Invalid server response.');
    }
    return json;
  }

  async function copyToClipboard(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        // fallback
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
      return true;
    } catch {
      return false;
    }
  }

  function buildGroupItem(group) {
    // DOM-safe, avoids XSS via innerHTML on untrusted text
    const wrap = document.createElement('div');
    wrap.className = 'group-item';

    const info = document.createElement('div');
    info.className = 'group-info';
    const name = document.createElement('div');
    name.className = 'group-name';
    name.textContent = group.name || '(no title)';
    const id = document.createElement('div');
    id.className = 'group-id';
    id.textContent = `ID: ${group.id}`;
    info.appendChild(name);
    info.appendChild(id);

    const type = document.createElement('div');
    type.className = 'group-type';
    type.textContent = group.type || 'Group';

    const actions = document.createElement('div');
    actions.className = 'group-actions';
    const btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.setAttribute('type', 'button');
    btn.dataset.id = group.id;
    btn.innerHTML = '<i class="fas fa-copy"></i> Copy ID';
    btn.addEventListener('click', async function() {
      const ok = await copyToClipboard(group.id);
      this.innerHTML = ok ? '<i class="fas fa-check"></i> Copied!' : '<i class="fas fa-times"></i> Failed';
      setTimeout(() => { this.innerHTML = '<i class="fas fa-copy"></i> Copy ID'; }, 2000);
    });
    actions.appendChild(btn);

    wrap.appendChild(info);
    wrap.appendChild(type);
    wrap.appendChild(actions);
    return wrap;
  }

  function displayGroups(groups) {
    const groupsList = document.getElementById('groupsList');
    groupsList.innerHTML = '';

    if (!groups || groups.length === 0) {
      const p = document.createElement('p');
      p.className = 'no-groups';
      p.textContent = 'No groups or channels found.';
      groupsList.appendChild(p);
    } else {
      groups.forEach(g => groupsList.appendChild(buildGroupItem(g)));
    }

    groupsContainer.style.display = 'block';
    listForm.style.display = 'none';
    h1Title.style.display = 'none';
    registerForm.style.display = 'block';

    // reflect completion
    listGroupsBtn.innerHTML = "<i class='fas fa-list'></i> Fetching is done!";
  }

  function checkFormFields(form, btnId) {
    const button = document.getElementById(btnId);
    const allFilled = [...form.querySelectorAll('input[required]')]
      .every(input => input.value.trim() !== '');
    button.disabled = !allFilled;
  }

  // --- Bind inputs to enable/disable buttons ---

  document.querySelectorAll('#listIdsForm input[required]').forEach(input => {
    input.addEventListener('input', () => checkFormFields(listForm, 'listGroupsBtn'));
  });

  document.querySelectorAll('#registerForm input[required]').forEach(input => {
    input.addEventListener('input', () => checkFormFields(registerForm, 'registerBtn'));
  });

  // --- Button handlers ---

  // Register config
  registerBtn.addEventListener('click', async function () {
    const formData = {
      user_id: document.getElementById('user_id').value,
      api_id: document.getElementById('api_id').value,
      api_hash: document.getElementById('api_hash').value,
      bot_token: document.getElementById('bot_token').value,
      source_group: document.getElementById('source_group').value,
      backup_group: document.getElementById('backup_group').value
    };

    // Validate before disabling anything
    for (const k in formData) {
      if (!formData[k]) {
        showMessage('Please fill all required fields', 'error');
        return;
      }
    }

    setFormEnabled(registerForm, false);
    try {
      const data = await safeFetch('/save_config', formData);
      if (data.status === 'success') {
        showMessage(data.message, 'success');
        registerForm.style.display = 'none';
        groupsContainer.style.display = 'none';
        // Show run bot button
        runBotButton.style.display = "block";
      } else {
        showMessage(data.message || 'Failed to save configuration.', 'error');
      }
    } catch (e) {
      showMessage('An error occurred: ' + e.message, 'error');
    } finally {
      setFormEnabled(registerForm, true);
    }
  });

  // List groups
  listGroupsBtn.addEventListener('click', async function () {
    const formData = {
      user_id: document.getElementById('user_id').value,
      api_id: document.getElementById('api_id').value,
      api_hash: document.getElementById('api_hash').value,
      username: document.getElementById('username').value,
      phone: document.getElementById('phone').value
    };

    // Validate before changing UI state
    for (const k in formData) {
      if (!formData[k]) {
        showMessage('Please fill all above required fields', 'error');
        return;
      }
    }

    // Busy state
    const originalContent = this.innerHTML;
    this.innerHTML = "<i class='fas fa-spinner fa-spin'></i> Fetching groups…";
    this.disabled = true;
    setFormEnabled(listForm, false);

    try {
      const data = await safeFetch('/get_groups', formData);
      if (data.status === 'success') {
        displayGroups(data.groups || []);
        showMessage('Groups fetched successfully.', 'success');
      } else {
        showMessage(data.message || 'Failed to fetch groups.', 'error');
        // let the user try again
        this.innerHTML = originalContent;
        this.disabled = false;
        setFormEnabled(listForm, true);
      }
    } catch (e) {
      showMessage('An error occurred: ' + e.message, 'error');
      this.innerHTML = originalContent;
      this.disabled = false;
      setFormEnabled(listForm, true);
    }
  });

  runBotBtn.addEventListener('click', async function () {
  try {
    const data = await safeFetch('/run_bot', {});
    if (data.status === 'success') {
      showMessage(data.message, 'success');
    } else {
      showMessage(data.message || 'Failed to start bot.', 'error');
    }
  } catch (e) {
    showMessage('An error occurred: ' + e.message, 'error');
  }
});

});
