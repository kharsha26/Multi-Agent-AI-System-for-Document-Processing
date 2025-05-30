import os
import uuid
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from agents.classifier_agent import ClassifierAgent
from memory.shared_memory import SharedMemory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="Multi-Agent Document Processor",
    description="AI system for processing PDF, JSON, and Email documents",
    version="1.0.0"
)

shared_memory = SharedMemory()
classifier_agent = ClassifierAgent(shared_memory)


@app.post("/process")
async def process_document(file: UploadFile = File(...)):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")

        filename = file.filename or "untitled"
        file_extension = filename.split('.')[-1].lower() if '.' in filename else ''

        if file_extension not in ["pdf", "json", "txt", "eml"]:
            raise HTTPException(status_code=415, detail="Unsupported file type")

        file_content = await file.read()

        result = classifier_agent.process(
            content=file_content,
            file_type=file_extension,
            doc_id=str(uuid.uuid4()),
            metadata={
                "filename": filename,
                "size": len(file_content)
            }
        )

        return JSONResponse(result)

    except Exception as e:
        logger.error(f"Processing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="File processing failed")


@app.get("/memory/{doc_id}")
async def get_memory(doc_id: str):
    try:
        memory_data = shared_memory.get_document_history(doc_id)
        if not memory_data:
            raise HTTPException(status_code=404, detail="Document not found")
        return JSONResponse(memory_data)
    except Exception as e:
        logger.error(f"Memory retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
