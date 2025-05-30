# agents/classifier_agent.py
from .base_agent import BaseAgent
import spacy
import re
import logging

logger = logging.getLogger(__name__)


class ClassifierAgent(BaseAgent):
    def __init__(self, shared_memory):
        super().__init__(shared_memory)

        from .email_agent import EmailAgent
        from .json_agent import JSONAgent
        from .pdf_agent import PDFAgent

        self.email_agent = EmailAgent(shared_memory)
        self.json_agent = JSONAgent(shared_memory)
        self.pdf_agent = PDFAgent(shared_memory)

        self.nlp = spacy.load("en_core_web_sm")

        self.intent_patterns = {
            "invoice":    [r"\binvoice\b",  r"\bpayment\b",        r"due\s+date"],
            "rfq":        [r"\brfq\b",      r"request\s+for\s+quote", r"\bquotation\b"],
            "complaint":  [r"\bcomplaint\b", r"\bdissatisfied\b",  r"\bissue\b"],
            "regulation": [r"\bregulation\b", r"\bcompliance\b",  r"\bstandard\b"],
            "syllabus":   [r"\bsyllabus\b", r"\bcurriculum\b",    r"course\s+outline"],
        }

    @staticmethod
    def is_email_content(text: str) -> bool:
        email_patterns = [
            r"^dear\s+\w+",
            r"regards,\s*$",
            r"sent\s+from\s+my\s+\w+",
        ]
        return any(
            re.search(pat, text, re.IGNORECASE | re.MULTILINE)
            for pat in email_patterns
        )

    def detect_intent(self, text: str) -> str:
        lowered = text.lower()
        for intent, patterns in self.intent_patterns.items():
            if any(re.search(pat, lowered) for pat in patterns):
                return intent

        doc = self.nlp(lowered)
        if any(tok.text in {"learn", "study", "course"} for tok in doc):
            return "syllabus"

        return "unknown"

    def extract_key_phrases(self, text: str, limit: int = 5) -> list:
        doc = self.nlp(text)
        phrases = set()

        phrases.update(
            chunk.text.strip()
            for chunk in doc.noun_chunks
            if len(chunk.text.split()) > 1
        )

        phrases.update(
            ent.text.strip()
            for ent in doc.ents
            if ent.label_ in {"ORG", "PRODUCT", "EVENT", "LAW"}
        )

        return list(phrases)[:limit]

    def process(self, content, file_type: str, doc_id: str, metadata=None):
        metadata = metadata or {}
        result = {
            "document_id": doc_id,
            "file_type": file_type,
            "metadata": metadata,
            "processing_steps": [],
            "key_phrases": [],
        }

        intent = "unknown"

        try:
            if file_type == "pdf":
                from utils.pdf_parser import extract_text_from_pdf

                text_content = extract_text_from_pdf(content)
                intent = self.detect_intent(text_content)
                result["key_phrases"] = self.extract_key_phrases(text_content)

                if self.is_email_content(text_content):
                    agent_result = self.email_agent.process(
                        text_content, doc_id, metadata | {"intent": intent}
                    )
                    result["processing_steps"].append(
                        {"agent": "email_agent", "result": agent_result}
                    )
                else:
                    agent_result = self.pdf_agent.process(
                        text_content, doc_id, metadata | {"intent": intent}
                    )
                    result["processing_steps"].append(
                        {"agent": "pdf_agent", "result": agent_result}
                    )

            elif file_type == "json":
                intent = metadata.get("intent", "unknown")
                agent_result = self.json_agent.process(content, doc_id, metadata)
                result["processing_steps"].append(
                    {"agent": "json_agent", "result": agent_result}
                )

            elif file_type in {"eml", "txt"}:
                if file_type == "eml":
                    from utils.email_parser import parse_email

                    email_data = parse_email(content)
                    content = email_data["body"]
                    metadata |= email_data

                intent = self.detect_intent(content)
                result["key_phrases"] = self.extract_key_phrases(content)

                agent_result = self.email_agent.process(
                    content, doc_id, metadata | {"intent": intent}
                )
                result["processing_steps"].append(
                    {"agent": "email_agent", "result": agent_result}
                )

            else:
                raise ValueError(f"Unsupported file_type '{file_type}'")

            self.update_memory(
                doc_id,
                {
                    "classification": {
                        "file_type": file_type,
                        "intent": intent,
                        "key_phrases": result["key_phrases"],
                    },
                    "metadata": metadata,
                },
            )

            return result

        except Exception as exc:
            logger.exception("Classification failed for %s: %s", doc_id, exc)
            raise
