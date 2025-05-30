# Multi-Agent AI Document Processing System

A sophisticated AI system that classifies and processes documents in PDF, JSON, or Email formats with shared context management.

## Features

- Classifies input documents by format and intent
- Routes to specialized agents (JSON, Email)
- Maintains shared context across processing
- Supports PDF, JSON, and Email formats
- Handles multiple intents (Invoice, RFQ, Complaint, etc.)

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Redis (optional for production)
4. Run: `python main.py`

## Sample Inputs

See `sample_inputs/` directory for example files to test the system.

## API Endpoints

- POST `/process` - Main processing endpoint
- GET `/memory/{doc_id}` - Retrieve processing history

## to run streamlit
streamlit run web_interface.py   