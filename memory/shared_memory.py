import json
import time
from typing import Dict, Any, Optional
import logging
import redis


class SharedMemory:
    def __init__(self, use_redis=False):
        self.logger = logging.getLogger("SharedMemory")
        self.use_redis = use_redis

        if use_redis:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
            try:
                self.redis_client.ping()
                self.logger.info("Connected to Redis")
            except redis.ConnectionError:
                self.logger.error("Failed to connect to Redis, falling back to in-memory")
                self.use_redis = False

        if not use_redis:
            self.in_memory_store = {}
            self.logger.info("Using in-memory storage")

    def update(self, doc_id: str, data: Dict[str, Any]):
        timestamp = time.time()
        document_data = {
            "timestamp": timestamp,
            "data": data,
            "doc_id": doc_id
        }

        if self.use_redis:
            self.redis_client.set(doc_id, json.dumps(document_data))
        else:
            self.in_memory_store[doc_id] = document_data

    def get_document_history(self, doc_id: str) -> Optional[Dict[str, Any]]:
        if self.use_redis:
            data = self.redis_client.get(doc_id)
            return json.loads(data) if data else None
        else:
            return self.in_memory_store.get(doc_id)

    def append_to_document(self, doc_id: str, new_data: Dict[str, Any]):
        existing = self.get_document_history(doc_id)
        if existing:
            if "extracted_fields" in existing["data"]:
                existing["data"]["extracted_fields"].update(new_data.get("extracted_fields", {}))
            else:
                existing["data"]["extracted_fields"] = new_data.get("extracted_fields", {})

            for key, value in new_data.items():
                if key != "extracted_fields":
                    existing["data"][key] = value

            self.update(doc_id, existing["data"])
        else:
            self.update(doc_id, new_data)