const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const browseBtn = document.getElementById('browse-btn');
const fileNameDisplay = document.getElementById('file-name');
const redactBtn = document.getElementById('redact-btn');
const statusMessage = document.getElementById('status-message');
const downloadSection = document.getElementById('download-section');

let selectedFile = null;

browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if(e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if(e.target.files.length) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    if (!file.name.endsWith('.docx')) {
        showMessage('Please upload a valid .docx file', 'error');
        return;
    }
    selectedFile = file;
    fileNameDisplay.textContent = file.name;
    redactBtn.disabled = false;
    downloadSection.classList.add('hidden');
    showMessage('', '');
}

redactBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    redactBtn.classList.add('loading');
    redactBtn.disabled = true;
    downloadSection.classList.add('hidden');
    showMessage('Processing document... Please wait.', '');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/api/redact', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Redaction failed');
        }

        const data = await response.json();
        
        document.getElementById('download-docx').href = data.docx_url;
        document.getElementById('download-report-md').href = data.report_md_url;
        document.getElementById('download-report-json').href = data.report_json_url;

        downloadSection.classList.remove('hidden');
        showMessage('Success! Your files are ready for download below.', 'success');

    } catch (error) {
        showMessage(error.message, 'error');
    } finally {
        redactBtn.classList.remove('loading');
        redactBtn.disabled = false;
    }
});

function showMessage(msg, type) {
    statusMessage.textContent = msg;
    statusMessage.className = 'status-message';
    if(type === 'success') statusMessage.classList.add('status-success');
    if(type === 'error') statusMessage.classList.add('status-error');
}
