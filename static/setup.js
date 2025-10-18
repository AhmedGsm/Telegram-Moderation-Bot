document.addEventListener('DOMContentLoaded', function () {

  // === ORIGINAL FUNCTIONALITY (Preserved) ===
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
  const codeInputs = document.querySelectorAll('.code-input');
  const fullCodeInput = document.getElementById('full-code');
  const dialog_overlay = document.querySelector('.dialog-overlay');
  let codeVerificationForm ;
  let messageContainer;
  let closeBtn ;
  let resendLink ;
  //const inputs = form.querySelectorAll('input[required]');
  let submitCodeBtn ;


  // --- Helpers ---
  function showMessage(message, type = 'success') {
    if (!messageBox) return;

    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`;
    messageBox.style.display = 'block';
    clearTimeout(showMessage._t);
    showMessage._t = setTimeout(() => {
      messageBox.style.display = 'none';
    }, 8000);
  }

  function setFormEnabled(formEl, enabled) {
    if (!formEl) return;
    [...formEl.querySelectorAll('input, button')].forEach(el => {
      el.disabled = !enabled;
    });
  }

  async function safeFetch(url, payload) {
    const headers = { 'Content-Type': 'application/json' };

    const res = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload || {})
    });
    let json;
    try {
      json = await res.json();
    } catch {
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
    btn.addEventListener('click', async function () {
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
    if (!groupsList) return;

    groupsList.innerHTML = '';

    if (!groups || groups.length === 0) {
      const p = document.createElement('p');
      p.className = 'no-groups';
      p.textContent = 'No groups or channels found.';
      groupsList.appendChild(p);
    } else {
      groups.forEach(g => groupsList.appendChild(buildGroupItem(g)));
    }

    if (groupsContainer) groupsContainer.style.display = 'block';
    if (listForm) listForm.style.display = 'none';
    if (h1Title) h1Title.style.display = 'none';
    if (registerForm) registerForm.style.display = 'block';

    // reflect completion
    if (listGroupsBtn) {
      listGroupsBtn.innerHTML = "<i class='fas fa-list'></i> Fetching is done!";
    }
  }

  function checkFormFields(form, btnId) {
    const button = document.getElementById(btnId);
    if (!button || !form) return;

    const allFilled = [...form.querySelectorAll('input[required]')]
      .every(input => input.value.trim() !== '');
    button.disabled = !allFilled;
  }

  // --- Bind inputs to enable/disable buttons ---
  if (listForm) {
    document.querySelectorAll('#listIdsForm input[required]').forEach(input => {
      input.addEventListener('input', () => checkFormFields(listForm, 'listGroupsBtn'));
    });
  }

  if (registerForm) {
    document.querySelectorAll('#registerForm input[required]').forEach(input => {
      input.addEventListener('input', () => checkFormFields(registerForm, 'registerBtn'));
    });
  }

  // --- Button handlers ---

  // Register config
  if (registerBtn) {
    registerBtn.addEventListener('click', async function () {
      const formData = {
        user_id: document.getElementById('user_id')?.value,
        api_id: document.getElementById('api_id')?.value,
        api_hash: document.getElementById('api_hash')?.value,
        bot_token: document.getElementById('bot_token')?.value,
        source_group: document.getElementById('source_group')?.value,
        backup_group: document.getElementById('backup_group')?.value
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
          if (registerForm) registerForm.style.display = 'none';
          if (groupsContainer) groupsContainer.style.display = 'none';
          // Show run bot button
          if (runBotButton) runBotButton.style.display = "block";
        } else {
          showMessage(data.message || 'Failed to save configuration.', 'error');
        }
      } catch (e) {
        showMessage('An error occurred: ' + e.message, 'error');
      } finally {
        setFormEnabled(registerForm, true);
      }
    });
  }

  // List groups
  if (listGroupsBtn) {
    listGroupsBtn.addEventListener('click', async function () {
      const formData = {
        user_id: document.getElementById('user_id')?.value,
        api_id: document.getElementById('api_id')?.value,
        api_hash: document.getElementById('api_hash')?.value,
        username: document.getElementById('username')?.value,
        phone: document.getElementById('phone')?.value
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
        }
        else if (data.status === 'code_required') {
          showMessage(data.message, 'success');
          // Display code introduction dialog
          dialog_overlay.style.display = "block";

          // Access elements DOM
          codeVerificationForm = document.getElementById('verification-form');
          messageContainer = document.querySelector('.message-container');
          submitCodeBtn = document.getElementById('verifyCodeBtn');
          closeBtn = document.querySelector('.close-btn');
          resendLink = document.getElementById('resend-link');

          // Send verification to the Flask App
          sendVerificationCode();

          // Event listener to the form submission
          codeVerificationFormEvent()

          // Launch event listeners
          setupEvents()

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
  }

  // Run bot
  if (runBotBtn) {
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
  }

  function sendVerificationCode() {
    // Verify code button (if exists)
    if (verifyCodeBtn) {
      verifyCodeBtn.addEventListener('click', async function () {
        const code = document.getElementById('full-code')?.value;
        if (!code) {
          showMessageVerificationCode('Please enter verification code', 'error');
          return;
        }

        try {
          const data = await safeFetch('/verify_code', { code: code });
          if (data.status === 'success') {
            showMessageVerificationCode(data.message, 'success');
            // Hide code verification dialog
            dialog_overlay.style.display = "none";
            // Display groups
            displayGroups(data.groups || []);
            showMessageVerificationCode('Groups fetched successfully.', 'success');
          } else {
            showMessageVerificationCode(data.message || 'Verification failed.', 'error');
          }
        } catch (e) {
          showMessageVerificationCode('An error occurred: ' + e.message, 'error');
        }
      });
    }
  }

  // Verify password button (if exists)
  if (verifyPasswordBtn) {
    verifyPasswordBtn.addEventListener('click', async function () {
      const password = document.getElementById('two_factor_password')?.value;
      if (!password) {
        showMessageVerificationCode('Please enter two-factor password', 'error');
        return;
      }

      try {
        const data = await safeFetch('/verify_2fa', { password: password });
        if (data.status === 'success') {
          showMessageVerificationCode(data.message, 'success');
          if (passwordVerification) passwordVerification.style.display = 'none';
        } else {
          showMessageVerificationCode(data.message || 'Two-factor authentication failed.', 'error');
        }
      } catch (e) {
        showMessageVerificationCode('An error occurred: ' + e.message, 'error');
      }
    });
  }

  // === Enhanced UI Features (New) ===
  function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {

      if (submitCodeBtn) {
        function validateForm() {
          const allFilled = Array.from(codeInputs).every(input => input.value.trim() !== '');
          submitCodeBtn.disabled = !allFilled;
        }

        codeInputs.forEach(input => {
          input.addEventListener('input', validateForm);
          input.addEventListener('blur', function () {
            if (!this.value.trim()) {
              this.style.borderColor = 'var(--error)';
            } else {
              this.style.borderColor = '';
            }
          });
        });

        validateForm();
      }
    });
  }

  setupFormValidation();

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // Add loading states to buttons
  function setButtonLoading(button, isLoading) {
    if (!button) return;

    if (isLoading) {
      button.dataset.originalText = button.innerHTML;
      button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
      button.disabled = true;
    } else {
      button.innerHTML = button.dataset.originalText;
      button.disabled = false;
    }
  }

  // Enhanced API call function with loading states
  async function safeFetchWithLoading(url, payload, button = null) {
    if (button) setButtonLoading(button, true);

    try {
      const data = await safeFetch(url, payload);
      return data;
    } finally {
      if (button) setButtonLoading(button, false);
    }
  }

  // Update existing buttons to use enhanced loading (optional)
  if (registerBtn) {
    const originalRegisterHandler = registerBtn.onclick;
    registerBtn.onclick = async function () {
      await safeFetchWithLoading('/save_config', {
        user_id: document.getElementById('user_id')?.value,
        api_id: document.getElementById('api_id')?.value,
        api_hash: document.getElementById('api_hash')?.value,
        bot_token: document.getElementById('bot_token')?.value,
        source_group: document.getElementById('source_group')?.value,
        backup_group: document.getElementById('backup_group')?.value
      }, registerBtn);

      // Call original handler logic
      if (typeof originalRegisterHandler === 'function') {
        originalRegisterHandler.call(this);
      }
    };
  }

  // Focus management for code inputs
  codeInputs.forEach((input, index) => {
    input.addEventListener('input', function () {
      if (this.value.length === 1) {
        this.classList.add('filled');
        if (index < codeInputs.length - 1) {
          codeInputs[index + 1].focus();
        }
      } else {
        this.classList.remove('filled');
      }
      updateFullCode();
    });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Backspace' && this.value === '' && index > 0) {
        codeInputs[index - 1].focus();
      }
    });
  });

  // Update the hidden input with the full code
  function updateFullCode() {
    let code = '';
    codeInputs.forEach(input => {
      code += input.value;
    });
    fullCodeInput.value = code;

    // Enable submit button only when all digits are entered
    submitCodeBtn.disabled = code.length !== 5;
  }

  // Form submission
  function codeVerificationFormEvent() {
    codeVerificationForm.addEventListener('submit', function (e) {
      e.preventDefault();

      const code = fullCodeInput.value;

      // Show loading state
      submitCodeBtn.disabled = true;
      submitCodeBtn.textContent = 'Verifying...';

      // Send to Flask backend for actual verification
      fetch('/verify_code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken() // If using CSRF protection
        },
        body: JSON.stringify({
          telegram_code: code
        })
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            showMessageVerificationCode('Verification successful!', 'success');
            // Redirect based on server response
            if (data.redirect_url) {
              setTimeout(() => {
                window.location.href = data.redirect_url;
              }, 1500);
            }
          } else {
            showMessageVerificationCode(data.error || 'Verification failed', 'error');
            submitCodeBtn.disabled = false;
            submitCodeBtn.textContent = 'Verify Code';
          }
        })
        .catch(error => {
          showMessageVerificationCode('Network error. Please try again.', 'error');
          submitBtn.disabled = false;
          submitBtn.textContent = 'Verify Code';
        });
    });
  }
  // Show message in the message container
  function showMessageVerificationCode(message, type) {
    messageContainer.textContent = message;
    messageContainer.className = 'message-container ' + type;

    let icon = 'ℹ️';
    if (type === 'error') icon = '❌';
    if (type === 'success') icon = '✅';

    messageContainer.innerHTML = `<span class="message-icon">${icon}</span> <span>${message}</span>`;
  }

  // Close button functionality
  function setupEvents() {
    closeBtn.addEventListener('click', function () {
      document.querySelector('.dialog-overlay').style.opacity = '0';
      /*setTimeout(() => {
        alert('Dialog closed. In a real application, this would close the overlay.');
        document.querySelector('.dialog-overlay').style.opacity = '1';
      }, 300);*/
    });

    // Resend code functionality
    resendLink.addEventListener('click', function (e) {
      e.preventDefault();
      showMessageVerificationCode('New verification code sent to your Telegram.', 'info');

      // In a real app, you would make an API call to resend the code
    });
  }
});