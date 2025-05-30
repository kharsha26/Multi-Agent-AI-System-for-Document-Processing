from agents.base_agent import BaseAgent
import json
from typing import Dict, Any
import logging

logger = logging.getLogger("JSONAgent")
class JSONAgent(BaseAgent):
    def __init__(self, shared_memory):
        super().__init__(shared_memory)

        self.target_schemas = {
            "invoice": {
                "required": ["invoice_number", "date", "total_amount", "vendor"],
                "optional": ["due_date", "tax_amount", "line_items"]
            },
            "rfq": {
                "required": ["rfq_number", "request_date", "items"],
                "optional": ["delivery_date", "special_requirements"]
            },
            "complaint": {
                "required": ["complaint_id", "date_received", "description"],
                "optional": ["customer_info", "resolution_requested"]
            }
        }

    def validate_json(self, json_data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        validation_result = {
            "is_valid": True,
            "missing_fields": [],
            "anomalies": []
        }

        for field in schema["required"]:
            if field not in json_data:
                validation_result["is_valid"] = False
                validation_result["missing_fields"].append(field)

        expected_fields = set(schema["required"] + schema["optional"])
        for field in json_data.keys():
            if field not in expected_fields:
                validation_result["anomalies"].append(f"Unexpected field: {field}")

        return validation_result

    def detect_intent(self, json_data: Dict[str, Any]) -> str:
        if "invoice_number" in json_data:
            return "invoice"
        elif "rfq_number" in json_data:
            return "rfq"
        elif "complaint_id" in json_data:
            return "complaint"
        else:
            return "unknown"

    def process(self, content: str, doc_id: str, metadata=None) -> Dict[str, Any]:
        metadata = metadata or {}
        result = {
            "document_id": doc_id,
            "agent": "json_agent",
            "extracted_fields": {},
            "metadata": metadata,
            "validation": {}
        }

        try:
            json_data = json.loads(content)

            intent = self.detect_intent(json_data)

            schema = self.target_schemas.get(intent, {})

            validation_result = self.validate_json(json_data, schema)

            result.update({
                "intent": intent,
                "extracted_fields": json_data,
                "validation": validation_result,
                "status": "processed"
            })

            memory_update = {
                "extracted_fields": json_data,
                "validation_result": validation_result,
                "processing_result": {
                    "agent": "json_agent",
                    "intent": intent
                }
            }
            self.update_memory(doc_id, memory_update)

            return result

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON: {str(e)}"
            logger.error(error_msg)
            result.update({
                "error": error_msg,
                "status": "failed"
            })
            self.update_memory(doc_id, {"error": error_msg})
            return result
        except Exception as e:
            logger.error(f"JSON processing failed for document {doc_id}: {str(e)}")
            result.update({
                "error": str(e),
                "status": "failed"
            })
            self.update_memory(doc_id, {"error": str(e)})
            return result