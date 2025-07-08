// Wait for the DOM to be fully loaded before attaching event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Get references to DOM elements we'll need
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    const uploadForm = document.getElementById('upload-form');
    const mergeBtn = document.getElementById('merge-btn');
    const clearBtn = document.getElementById('clear-btn');
    const alertDiv = document.getElementById('alert');

    /**
     * Display an alert message to the user
     * @param {string} message - The message to display
     * @param {string} type - The type of alert ('error' or 'success')
     */
    function showAlert(message, type = 'error') {
        alertDiv.textContent = message;
        alertDiv.className = `alert ${type}`;
        alertDiv.style.display = 'block';
        // Hide the alert after 5 seconds
        setTimeout(() => {
            alertDiv.style.display = 'none';
        }, 5000);
    }

    /**
     * Update the state of merge and clear buttons based on file list
     */
    function updateButtons() {
        const hasFiles = fileList.children.length > 0;
        mergeBtn.disabled = !hasFiles;
        clearBtn.disabled = !hasFiles;
    }

    /**
     * Add a new file item to the file list
     * @param {Object} fileInfo - Information about the file
     * @param {string} fileInfo.id - Unique identifier for the file
     * @param {string} fileInfo.name - Name of the file
     */
    function addFileToList(fileInfo) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.dataset.fileId = fileInfo.id;
        fileItem.innerHTML = `
            <i class="fas fa-file-pdf"></i>
            <span>${fileInfo.name}</span>
            <button type="button" class="remove-file" onclick="removeFile('${fileInfo.id}')">
                <i class="fas fa-times"></i>
            </button>
        `;
        fileList.appendChild(fileItem);
        updateButtons();
    }

    // Handle file selection
    fileInput.addEventListener('change', async () => {
        // Create FormData object to send files to server
        const formData = new FormData();
        Array.from(fileInput.files).forEach(file => {
            formData.append('files[]', file);
        });

        try {
            // Send files to server
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error);
            }

            // Add each uploaded file to the list
            data.files.forEach(file => addFileToList(file));
            showAlert('Files uploaded successfully', 'success');
        } catch (error) {
            showAlert(error.message);
        }

        // Reset file input to allow selecting the same file again
        fileInput.value = '';
    });
});

/**
 * Remove a file from the list and server
 * @param {string} fileId - The ID of the file to remove
 */
async function removeFile(fileId) {
    try {
        const response = await fetch(`/remove/${fileId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error);
        }

        // Remove file item from the UI
        const fileItem = document.querySelector(`[data-file-id="${fileId}"]`);
        if (fileItem) {
            fileItem.remove();
        }

        // Update button states
        const fileList = document.getElementById('file-list');
        const mergeBtn = document.getElementById('merge-btn');
        const clearBtn = document.getElementById('clear-btn');
        const hasFiles = fileList.children.length > 0;
        mergeBtn.disabled = !hasFiles;
        clearBtn.disabled = !hasFiles;

    } catch (error) {
        showAlert(error.message);
    }
}

/**
 * Clear all files from the list and server
 */
async function clearFiles() {
    try {
        const response = await fetch('/clear', {
            method: 'POST'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error);
        }

        // Clear the file list and disable buttons
        const fileList = document.getElementById('file-list');
        fileList.innerHTML = '';
        const mergeBtn = document.getElementById('merge-btn');
        const clearBtn = document.getElementById('clear-btn');
        mergeBtn.disabled = true;
        clearBtn.disabled = true;

    } catch (error) {
        showAlert(error.message);
    }
}

/**
 * Merge all files in the list
 */
async function mergeFiles() {
    try {
        const response = await fetch('/merge', {
            method: 'POST'
        });

        if (response.ok) {
            // Create and trigger download of merged PDF
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'merged.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            // Clear the file list after successful merge
            const fileList = document.getElementById('file-list');
            fileList.innerHTML = '';
            const mergeBtn = document.getElementById('merge-btn');
            const clearBtn = document.getElementById('clear-btn');
            mergeBtn.disabled = true;
            clearBtn.disabled = true;
        } else {
            const data = await response.json();
            throw new Error(data.error);
        }
    } catch (error) {
        showAlert(error.message);
    }
}

/**
 * Display an alert message to the user
 * @param {string} message - The message to display
 * @param {string} type - The type of alert ('error' or 'success')
 */
function showAlert(message, type = 'error') {
    const alertDiv = document.getElementById('alert');
    alertDiv.textContent = message;
    alertDiv.className = `alert ${type}`;
    alertDiv.style.display = 'block';
    setTimeout(() => {
        alertDiv.style.display = 'none';
    }, 5000);
}
