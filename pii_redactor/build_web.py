import os

FILES = {
    "app.py": """\
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from document.docx_redactor import redact_document
import os
import shutil
import uuid

app = FastAPI()

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static directories
app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")

@app.post("/api/redact")
async def redact_api(file: UploadFile = File(...)):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")
    
    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    output_filename = f"redacted_{file_id}_{file.filename}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    try:
        redact_document(input_path, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {
        "docx_url": f"/output/{output_filename}",
        "report_md_url": "/output/evaluation_report.md",
        "report_json_url": "/output/evaluation_report.json"
    }

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")
""",
    "frontend/index.html": """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PII Redactor</title>
    <link rel="stylesheet" href="/static/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
</head>
<body>
    <div class="background-animation"></div>
    <div class="container">
        <header>
            <h1>Shield<span class="highlight">PII</span></h1>
            <p>Intelligent, Format-Preserving Redaction</p>
        </header>

        <main>
            <div class="upload-box" id="drop-zone">
                <input type="file" id="file-input" accept=".docx" hidden>
                <div class="icon">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="17 8 12 3 7 8"></polyline>
                        <line x1="12" y1="3" x2="12" y2="15"></line>
                    </svg>
                </div>
                <h2>Drag & Drop your .docx file</h2>
                <p>or</p>
                <button class="btn-primary" id="browse-btn">Browse Files</button>
                <p class="file-name" id="file-name"></p>
            </div>

            <div class="action-section">
                <button class="btn-glow" id="redact-btn" disabled>
                    <span class="btn-text">Redact Document</span>
                    <div class="spinner" id="spinner"></div>
                </button>
            </div>

            <div class="status-message" id="status-message"></div>

            <div class="download-section hidden" id="download-section">
                <h3>Ready for Download</h3>
                <div class="download-grid">
                    <a id="download-docx" href="#" class="download-card docx-card" download>
                        <div class="dl-icon">📄</div>
                        <div class="dl-info">
                            <h4>Redacted DOCX</h4>
                            <p>Cleaned document</p>
                        </div>
                    </a>
                    <a id="download-report-md" href="#" class="download-card report-card" download>
                        <div class="dl-icon">📊</div>
                        <div class="dl-info">
                            <h4>Evaluation Report</h4>
                            <p>Markdown metrics</p>
                        </div>
                    </a>
                    <a id="download-report-json" href="#" class="download-card json-card" download>
                        <div class="dl-icon">⚙️</div>
                        <div class="dl-info">
                            <h4>Evaluation JSON</h4>
                            <p>Raw data format</p>
                        </div>
                    </a>
                </div>
            </div>
        </main>
    </div>
    <script src="/static/script.js"></script>
</body>
</html>
""",
    "frontend/style.css": """\
:root {
    --primary: #6366f1;
    --primary-hover: #4f46e5;
    --accent: #0ea5e9;
    --bg-dark: #0f172a;
    --glass-bg: rgba(30, 41, 59, 0.7);
    --glass-border: rgba(255, 255, 255, 0.1);
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-dark);
    color: var(--text-main);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}

.background-animation {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.15), transparent 40%),
                radial-gradient(circle at 80% 20%, rgba(14, 165, 233, 0.15), transparent 30%);
    animation: rotate 20s linear infinite;
    z-index: -1;
}

@keyframes rotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.container {
    width: 100%;
    max-width: 600px;
    padding: 2rem;
    background: var(--glass-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    text-align: center;
    transform: translateY(20px);
    opacity: 0;
    animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes slideUp {
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

header h1 {
    font-size: 2.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.highlight {
    color: transparent;
    background: linear-gradient(90deg, var(--primary), var(--accent));
    -webkit-background-clip: text;
    background-clip: text;
}

header p {
    color: var(--text-muted);
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

.upload-box {
    border: 2px dashed var(--glass-border);
    border-radius: 16px;
    padding: 3rem 2rem;
    background: rgba(255,255,255,0.02);
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.upload-box:hover, .upload-box.dragover {
    border-color: var(--primary);
    background: rgba(99, 102, 241, 0.05);
}

.icon {
    color: var(--primary);
    margin-bottom: 1rem;
    transition: transform 0.3s ease;
}

.upload-box:hover .icon {
    transform: translateY(-5px);
}

.upload-box h2 {
    font-size: 1.2rem;
    font-weight: 400;
    margin-bottom: 0.5rem;
}

.upload-box p {
    color: var(--text-muted);
    margin-bottom: 1rem;
}

.btn-primary {
    background: var(--glass-border);
    color: var(--text-main);
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-primary:hover {
    background: rgba(255,255,255,0.15);
}

.file-name {
    margin-top: 1rem;
    font-size: 0.9rem;
    color: var(--accent) !important;
    font-weight: 600;
}

.action-section {
    margin-top: 2rem;
}

.btn-glow {
    position: relative;
    background: linear-gradient(90deg, var(--primary), var(--accent));
    color: white;
    border: none;
    padding: 1rem 3rem;
    font-size: 1.2rem;
    font-weight: 600;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    overflow: hidden;
    width: 100%;
}

.btn-glow::before {
    content: '';
    position: absolute;
    top: 0; left: -100%; width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s ease;
}

.btn-glow:hover::before {
    left: 100%;
}

.btn-glow:disabled {
    background: var(--glass-border);
    color: var(--text-muted);
    cursor: not-allowed;
    box-shadow: none;
}

.spinner {
    display: none;
    width: 24px;
    height: 24px;
    border: 3px solid rgba(255,255,255,0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s ease-in-out infinite;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}

.btn-glow.loading .btn-text {
    opacity: 0;
}

.btn-glow.loading .spinner {
    display: block;
}

@keyframes spin {
    to { transform: translate(-50%, -50%) rotate(360deg); }
}

.status-message {
    margin-top: 1rem;
    font-size: 1rem;
    min-height: 24px;
    transition: color 0.3s ease;
}
.status-success { color: #10b981; }
.status-error { color: #ef4444; }

/* Download Section */
.download-section {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid var(--glass-border);
    animation: fadeIn 0.5s ease;
}

.hidden {
    display: none;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

.download-section h3 {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--text-main);
}

.download-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
}

.download-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 1rem;
    text-decoration: none;
    color: var(--text-main);
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: all 0.3s ease;
}

.download-card:hover {
    transform: translateY(-5px);
    background: rgba(255, 255, 255, 0.1);
    box-shadow: 0 10px 20px -5px rgba(0,0,0,0.3);
}

.docx-card:hover { border-color: #3b82f6; }
.report-card:hover { border-color: #10b981; }
.json-card:hover { border-color: #f59e0b; }

.dl-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.dl-info h4 {
    font-size: 0.95rem;
    margin-bottom: 0.25rem;
}

.dl-info p {
    font-size: 0.8rem;
    color: var(--text-muted);
}
""",
    "frontend/script.js": """\
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
"""
}

for filepath, content in FILES.items():
    dirname = os.path.dirname(filepath)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filepath}")
