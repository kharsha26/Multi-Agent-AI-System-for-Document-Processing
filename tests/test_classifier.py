import pytest
from agents.classifier_agent import ClassifierAgent
from memory.shared_memory import SharedMemory


@pytest.fixture
def classifier_agent():
    shared_memory = SharedMemory()
    return ClassifierAgent(shared_memory)


def test_detect_intent(classifier_agent):
    # Test invoice intent
    invoice_text = "Please find attached invoice INV-123 for $100. Due date: 2023-12-01"
    assert classifier_agent.detect_intent(invoice_text) == "invoice"

    # Test RFQ intent
    rfq_text = "We are requesting a quote for 100 units of product X"
    assert classifier_agent.detect_intent(rfq_text) == "rfq"

    # Test complaint intent
    complaint_text = "I'm writing to complain about poor service received last week"
    assert classifier_agent.detect_intent(complaint_text) == "complaint"