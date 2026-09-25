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

@app.get("/api/download-project")
async def download_project():
    return FileResponse("project.zip", media_type="application/zip", filename="pii_redactor.zip")

@app.get("/api/download-evaluation-doc")
async def download_eval_doc():
    return FileResponse("README_Explanation.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="Evaluation_Strategy_and_Metrics.docx")

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")
