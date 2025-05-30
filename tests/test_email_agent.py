import pytest
from agents.email_agent import EmailAgent
from memory.shared_memory import SharedMemory


@pytest.fixture
def email_agent():
    shared_memory = SharedMemory()
    return EmailAgent(shared_memory)


def test_extract_entities(email_agent):
    email_text = """
    From: sender@example.com
    To: recipient@company.com

    This is an urgent email about our meeting on 15/11/2023.
    Can you confirm your availability? What time would work best?
    """

    entities = email_agent.extract_entities(email_text)

    assert entities["sender"] == "sender@example.com"
    assert entities["recipient"] == "recipient@company.com"
    assert entities["date"] == "15/11/2023"
    assert entities["urgency"] == "high"
    assert len(entities["key_phrases"]) > 0