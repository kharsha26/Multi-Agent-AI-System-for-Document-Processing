from agents import BaseAgent
from typing import Dict, Any

class PDFAgent(BaseAgent):
    def __init__(self, shared_memory):
        super().__init__(shared_memory)

    def process(self, content: str, doc_id: str, metadata=None) -> Dict[str, Any]:
        """Process PDF content"""
        metadata = metadata or {}
        result = {
            "document_id": doc_id,
            "agent": "pdf_agent",
            "content_type": "pdf",
            "pages": len(content.split('\f')) if '\f' in content else 1,
            "status": "processed"
        }

        self.update_memory(doc_id, {
            "pdf_processing": result,
            "metadata": metadata
        })

        return result
