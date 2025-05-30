from agents.base_agent import BaseAgent
import re
from typing import Dict, Any
import logging

logger = logging.getLogger("EmailAgent")


class EmailAgent(BaseAgent):
    def __init__(self, shared_memory):
        super().__init__(shared_memory)

    def extract_entities(self, text: str) -> Dict[str, Any]:
        entities = {
            "sender": None,
            "recipient": None,
            "date": None,
            "urgency": "normal",
            "key_phrases": []
        }

        email_pattern = r'[\w\.-]+@[\w\.-]+'
        emails = re.findall(email_pattern, text)
        if emails:
            entities["sender"] = emails[0]  # First email is likely sender
            if len(emails) > 1:
                entities["recipient"] = emails[1]

        date_pattern = r'\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}\s+[A-Za-z]+\s+\d{4}'
        dates = re.findall(date_pattern, text)
        if dates:
            entities["date"] = dates[0]

        urgent_keywords = ['urgent', 'asap', 'immediately', 'important']
        if any(keyword in text.lower() for keyword in urgent_keywords):
            entities["urgency"] = "high"

        question_pattern = r'\b(how|what|when|where|why|who|can|could|would|will)\b[\w\s,]*\?'
        questions = re.findall(question_pattern, text, re.IGNORECASE)
        entities["key_phrases"] = questions[:3]  # Limit to 3 questions

        return entities

    def determine_crm_action(self, intent: str, phrases: list) -> str:
        """Enhanced CRM action determination"""
        action_map = {
            "invoice": "create_billing_record",
            "rfq": "create_opportunity",
            "complaint": "create_support_case",
            "regulation": "store_in_knowledge_base",
            "syllabus": "store_in_learning_materials",
            "default": "create_ticket"
        }

        # Special handling for regulations with specific phrases
        if intent == "regulation":
            legal_terms = {"gdpr", "hipaa", "sox"}
            if any(term in (phrase.lower() for phrase in phrases) for term in legal_terms):
                return "create_compliance_alert"

        return action_map.get(intent, action_map["default"])

    def process(self, content: str, doc_id: str, metadata=None) -> Dict[str, Any]:
        """Enhanced email processing"""
        metadata = metadata or {}
        try:
            entities = self.extract_entities(content)
            intent = metadata.get("intent", "unknown")
            phrases = metadata.get("key_phrases", [])

            result = {
                "document_id": doc_id,
                "agent": "email_agent",
                "extracted_fields": entities,
                "crm_action": self.determine_crm_action(intent, phrases),
                "key_phrases": phrases,
                "status": "processed"
            }

            self.update_memory(doc_id, {
                "email_processing": result,
                "metadata": metadata
            })

            return result

        except Exception as e:
            logger.error(f"Email processing failed for document {doc_id}: {str(e)}")
            error_result = {
                "error": str(e),
                "document_id": doc_id,
                "status": "failed"
            }
            self.update_memory(doc_id, {"error": str(e)})
            return error_result
