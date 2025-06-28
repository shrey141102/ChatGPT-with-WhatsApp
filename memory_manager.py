from mem0 import MemoryClient
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    """Simple memory manager using Mem0."""
    
    def __init__(self, api_key):
        self.client = MemoryClient(api_key=api_key)
        logger.info("🧠 Memory manager initialized")
    
    def store_conversation(self, user_id, user_message, ai_response):
        """Store conversation in memory."""
        try:
            messages = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": ai_response}
            ]
            
            result = self.client.add(messages, user_id=user_id)
            logger.info(f"💾 Stored memory for {user_id}: {result}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Memory storage error for {user_id}: {e}")
            return False
    
    def get_user_context(self, user_id):
        """Get relevant context from user's memory."""
        try:
            # Search for recent conversation context
            results = self.client.search(
                "recent conversation preferences personal information", 
                user_id=user_id,
                limit=3
            )
            
            if results:
                context_parts = []
                for result in results:
                    memory = result.get("memory", "")
                    if memory:
                        context_parts.append(memory)
                        logger.info(f"🔍 Found memory: {memory[:50]}...")
                
                if context_parts:
                    return " | ".join(context_parts)
            
            return ""
            
        except Exception as e:
            logger.error(f"❌ Context retrieval error for {user_id}: {e}")
            return ""
    
    def search_memories(self, user_id, query, limit=5):
        """Search user's memories."""
        try:
            results = self.client.search(query, user_id=user_id, limit=limit)
            logger.info(f"🔍 Search '{query}' for {user_id}: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Memory search error: {e}")
            return []