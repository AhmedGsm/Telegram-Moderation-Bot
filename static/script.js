// static/script.js
document.addEventListener('DOMContentLoaded', function() {
    const registerBtn = document.getElementById('registerBtn');
    const listGroupsBtn = document.getElementById('listGroupsBtn');
    const verifyCodeBtn = document.getElementById('verifyCodeBtn');
    const verifyPasswordBtn = document.getElementById('verifyPasswordBtn');
    const messageBox = document.getElementById('messageBox');
    const groupsContainer = document.getElementById('groupsContainer');
    const codeVerification = document.getElementById('codeVerification');
    const passwordVerification = document.getElementById('passwordVerification');
    const listForm = document.getElementById("listIdsForm");
    const registerForm = document.getElementById("registerForm");

    // Show message in message box
    function showMessage(message, type) {
        messageBox.textContent = message;
        messageBox.className = `message-box ${type}`;
        setTimeout(() => {
            messageBox.style.display = 'none';
        }, 10000);
    }

    // Register button click handler
    registerBtn.addEventListener('click', function() {
        const formData = {
            user_id: document.getElementById('user_id').value,
            api_id: document.getElementById('api_id').value,
            api_hash: document.getElementById('api_hash').value,
            bot_token: document.getElementById('bot_token').value,
            source_group: document.getElementById('source_group').value,
            backup_group: document.getElementById('backup_group').value
        };

        // Validate all fields
        for (const key in formData) {
            if (!formData[key]) {
                showMessage('Please fill all required fields', 'error');
                return;
            }
        }

        // Send data to server
        fetch('/save_config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showMessage(data.message, 'success');
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(error => {
            showMessage('An error occurred: ' + error, 'error');
        });

        // Hide  register form after submission
        registerForm.style.display = "none";

        // Hide groups list container after submission
        groupsContainer.style.display = 'none';
    });

    // List Groups button click handler
    listGroupsBtn.addEventListener('click', function() {
        const formData = {
            user_id: document.getElementById('user_id').value,
            api_id: document.getElementById('api_id').value,
            api_hash: document.getElementById('api_hash').value,
            username: document.getElementById('username').value,
            phone: document.getElementById('phone').value
        };
        
        // Change to Please wait while fetching groups
        this.innerHTML = "<i class='fas fa-wait'></i> Please Wait while fetching groups IDs...";

        // Disable button
        listGroupsBtn.disabled = true

        // Disable all form fields after clicking on list button
        const formFields = document.querySelectorAll("#listIdsForm input");
        formFields.forEach(field => {
            field.disabled = true;
        });

        // Validate all fields
        for (const key in formData) {
            if (!formData[key]) {
                showMessage('Please fill all above required fields', 'error');
                return;
            }
        }

        // Send data to server
        fetch('/get_groups', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayGroups(data.groups);
            } else if (data.status === 'code_required') {
                codeVerification.style.display = 'block';
                document.getElementById('verificationMessage').textContent = data.message;
                showMessage(data.message, 'success');
            } else if (data.status === 'password_required') {
                passwordVerification.style.display = 'block';
                showMessage(data.message, 'success');
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(error => {
            showMessage('An error occurred: ' + error, 'error');
        });

    });

    // Verify code button click handler
    verifyCodeBtn.addEventListener('click', function() {
        const code = document.getElementById('verificationCode').value;

        if (!code) {
            showMessage('Please enter the verification code', 'error');
            return;
        }

        fetch('/verify_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code: code })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                codeVerification.style.display = 'none';
                displayGroups(data.groups);
                showMessage('Verification successful!', 'success');
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(error => {
            showMessage('An error occurred: ' + error, 'error');
        });
    });

    // Verify password button click handler
    verifyPasswordBtn.addEventListener('click', function() {
        const password = document.getElementById('password').value;

        if (!password) {
            showMessage('Please enter your password', 'error');
            return;
        }

        fetch('/verify_password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password: password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                passwordVerification.style.display = 'none';
                displayGroups(data.groups);
                showMessage('Verification successful!', 'success');
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(error => {
            showMessage('An error occurred: ' + error, 'error');
        });
    });

    // Display groups in the groups container
    function displayGroups(groups) {
        const groupsList = document.getElementById('groupsList');
        groupsList.innerHTML = '';

        if (groups.length === 0) {
            groupsList.innerHTML = '<p class="no-groups">No groups or channels found.</p>';
            groupsContainer.style.display = 'block';
            return;
        }

        groups.forEach(group => {
            const groupItem = document.createElement('div');
            groupItem.className = 'group-item';

            groupItem.innerHTML = `
                <div class="group-info">
                    <div class="group-name">${group.name}</div>
                    <div class="group-id">ID: ${group.id}</div>
                </div>
                <div class="group-type">${group.type}</div>
                <div class="group-actions">
                    <button class="copy-btn" data-id="${group.id}">
                        <i class="fas fa-copy"></i> Copy ID
                    </button>
                </div>
            `;

            groupsList.appendChild(groupItem);
        });

        // Add event listeners to copy buttons
        document.querySelectorAll('.copy-btn').forEach(button => {
            button.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                copyToClipboard(id);
                this.innerHTML = '<i class="fas fa-check"></i> Copied!';

                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-copy"></i> Copy ID';
                }, 2000);
            });
        });

        groupsContainer.style.display = 'block';
        listForm.style.display = 'none';
        registerForm.style.display = 'block';

        // Change button content when fetching is done!
        listGroupsBtn.innerHTML = "<i class='fas fa-list'></i> Fetching is done!";

    }

    // Copy text to clipboard
    function copyToClipboard(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }

    // Function to check if all required inputs are filled
    function checkFormFields(form, btn) {
    const button = document.getElementById(btn);

    // Check all required inputs
    const allFilled = [...form.querySelectorAll("input[required]")]
        .every(input => input.value.trim() !== "");

    // Enable/disable button
    button.disabled = !allFilled;
    }

    // Attach event listeners to inputs (List group IDs form)

    const listBtn = "listGroupsBtn"
    document.querySelectorAll("#listIdsForm input[required]").forEach(input => {
    input.addEventListener("input", () => checkFormFields(listForm, listBtn));
    });

    // Attach event listeners to inputs (Register form)
    const regBtn = "registerBtn"
    document.querySelectorAll("#registerForm input[required]").forEach(input => {
    input.addEventListener("input", () => checkFormFields(registerForm, regBtn));
    });

});