import pytest
import json
from agents.json_agent import JSONAgent
from memory.shared_memory import SharedMemory


@pytest.fixture
def json_agent():
    shared_memory = SharedMemory()
    return JSONAgent(shared_memory)


def test_process_json(json_agent):
    # Test valid invoice JSON
    invoice_json = json.dumps({
        "invoice_number": "INV-123",
        "date": "2023-11-01",
        "total_amount": 100.0,
        "vendor": "Acme Corp"
    })

    result = json_agent.process(invoice_json, "test-doc-1")
    assert result["status"] == "processed"
    assert result["intent"] == "invoice"
    assert result["validation"]["is_valid"] == True