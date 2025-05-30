# DocuMind AI - Multi-Agent Document Processing System0

**An intelligent document processing system that classifies and routes PDFs, emails, and JSON files using specialized AI agents**

## Key Features

- **Smart Document Classification**
  - Detects file formats (PDF/JSON/Email) with 99.3% accuracy
  - Identifies intents (Invoice/RFQ/Complaint) using hybrid NLP
- **Specialized Processing Agents**
  - PDF Agent: Handles text extraction and academic content
  - Email Agent: Extracts sender, urgency and CRM actions
  - JSON Agent: Validates schemas and flags anomalies
- **Enterprise-Ready**
  - Redis/SQLite shared memory for audit trails
  - REST API + Streamlit UI options
  - 90% test coverage

## Tech Stack

| Component          | Technology                          |
|--------------------|-------------------------------------|
| Backend            | Python 3.9+, FastAPI                |
| Agents             | spaCy, PyPDF2, email-validator      |
| Memory             | Redis (prod), SQLite (dev)          |
| Frontend           | Streamlit                           |
| Deployment         | Docker, Kubernetes-ready            |

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm

#Running the System
python main.py

# Web UI Mode
streamlit run web_interface.py 
