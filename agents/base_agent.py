# agents/base_agent.py
from abc import ABC, abstractmethod
import logging
class BaseAgent(ABC):
    def __init__(self, shared_memory):
        self.shared_memory = shared_memory
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def process(self, content, doc_id, metadata=None):
        pass

    def update_memory(self, doc_id, data):
        try:
            self.shared_memory.update(doc_id, data)
            self.logger.info(f"Updated memory for document {doc_id}")
        except Exception as e:
            self.logger.error(f"Failed to update memory: {str(e)}")
            raise