document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('convert-form');
    const urlGroup = document.getElementById('url-group');
    const textGroup = document.getElementById('text-group');
    const toggleBtn = document.getElementById('toggle-fallback-btn');
    const convertBtn = document.getElementById('convert-btn');
    const statusContainer = document.getElementById('status-container');
    const statusMessage = document.getElementById('status-message');

    let isFallbackMode = false;

    // Toggle between URL and Text fallback
    toggleBtn.addEventListener('click', () => {
        isFallbackMode = !isFallbackMode;
        if (isFallbackMode) {
            urlGroup.classList.add('hidden');
            textGroup.classList.remove('hidden');
            toggleBtn.textContent = 'Want to try a link instead?';
            document.getElementById('chat-text').focus();
        } else {
            textGroup.classList.add('hidden');
            urlGroup.classList.remove('hidden');
            toggleBtn.textContent = 'Link not working? Paste text instead.';
            document.getElementById('chat-url').focus();
        }
    });

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const urlInput = document.getElementById('chat-url').value.trim();
        const textInput = document.getElementById('chat-text').value.trim();

        // Basic client-side validation
        if (!isFallbackMode && !urlInput) {
            showStatus('Please enter a shared conversation link.', true);
            return;
        }
        if (isFallbackMode && !textInput) {
            showStatus('Please paste your conversation text.', true);
            return;
        }

        // Prepare the payload
        const payload = {
            method: isFallbackMode ? 'text' : 'url',
            data: isFallbackMode ? textInput : urlInput
        };

        // Update UI to loading state
        convertBtn.disabled = true;
        convertBtn.textContent = 'Processing...';
        showStatus('Connecting to server...', false);

        try {
            // We will point this to our FastAPI route
            const response = await fetch('/api/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            // Check if the response is a PDF file
            const contentType = response.headers.get('content-type');
            
            if (response.ok && contentType && contentType.includes('application/pdf')) {
                // Handle file download
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                
                // Try to get filename from headers, fallback to default
                let filename = 'afterchat-conversation.pdf';
                const disposition = response.headers.get('content-disposition');
                if (disposition && disposition.indexOf('attachment') !== -1) {
                    const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                    const matches = filenameRegex.exec(disposition);
                    if (matches != null && matches[1]) { 
                        filename = matches[1].replace(/['"]/g, '');
                    }
                }
                
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(downloadUrl);
                
                showStatus('PDF generated successfully.', false);
            } else {
                // If not a PDF, it's likely a JSON error message from the backend
                const errorData = await response.json();
                showStatus(errorData.detail || errorData.message || 'Conversion failed. Please try the text fallback.', true);
            }
        } catch (error) {
            console.error('Network or parsing error:', error);
            showStatus('A network error occurred. Is the server running?', true);
        } finally {
            // Restore UI state
            convertBtn.disabled = false;
            convertBtn.textContent = 'Convert to PDF';
        }
    });

    function showStatus(message, isError) {
        statusContainer.classList.remove('hidden');
        statusMessage.textContent = message;
        statusMessage.style.color = isError ? '#D9534F' : 'var(--text-secondary)'; // Muted red for errors
    }
});