#backend/workers/vllm_request_worker.py
import asyncio
import json

import httpx
from repository.user_config import UserConfigRepository
from database import SessionLocal  
from models.message import Message
from repository.message import MessageRepository
from event_broker.redis import dequeue_task, publish_stream_event, redis_client
from constants import TASK_QUEUE_NAME, LLM_API_URL, SYSTEM_PROMPT, MAX_LLM_TOKENS
from core.logger import logger


DLQ_NAME = f"{TASK_QUEUE_NAME}_dlq"

async def process_task(task_data: dict):
    # TODO: Add error handling and retries for VLLM processing, using priority queues or a dead-letter queue (DLQ) for failed tasks.
    
    chat_id = task_data["chat_id"]
    user_id = task_data["user_id"]
    original_message_id = task_data["message_id"]

    # logger.info(f"Processing task for chat {chat_id}, user {user_id}")

    # send request to vllm
    
    async with SessionLocal() as session:
        message_repo = MessageRepository(session)
        user_config_repo = UserConfigRepository(session)
        
        # fetch chat history to build context
        history = await message_repo.get_by_chat_id(chat_id)
        user_config = await user_config_repo.get_by_user_id(user_id)
        
        dynamic_system_prompt = SYSTEM_PROMPT
        
        if user_config and user_config.personalized_prompt:
            dynamic_system_prompt += f"\n\nUser Instructions:\n{user_config.personalized_prompt}"
            
        messages_payload = [
            {"role": "system", "content": dynamic_system_prompt}
        ]
        
        for m in history:
            messages_payload.append({"role": m.role, "content": m.content})            
            
        requested_model = history[-1].model
        

    full_response = ""
    token_count = 0
    
    payload = {
        "model": requested_model,
        "messages": messages_payload,
        "stream": True,
        "max_tokens": MAX_LLM_TOKENS
    } 


    try:
        async with httpx.AsyncClient(timeout=120) as client: 
            async with client.stream("POST", LLM_API_URL, json=payload) as response:
                
                # Capture the actual error message from the API before raising
                if response.status_code >= 400:
                    await response.aread() # Read the error body
                    api_error = response.text
                    error_msg = f"API returned {response.status_code}: {api_error}"
                    logger.error(f"LLM API Error for chat {chat_id}: {error_msg}")
                    raise Exception(error_msg) # Pass the detailed message to the DLQ
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        else:
                            try:
                                data_dict = json.loads(data)
                                delta = data_dict["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    full_response += content
                                    token_count += 1
                                    await publish_stream_event(chat_id=chat_id, token=content, is_finished=False)
                            except json.JSONDecodeError as e:
                                # Include the raw data that failed to parse
                                logger.error(f"JSON decode error for chat {chat_id}. Raw data: '{data}'. Error: {e}")
                                
    except httpx.RequestError as e:
        # Catch connection issues (e.g., vLLM is offline, DNS failure, timeouts)
        error_msg = f"Network error connecting to LLM API for chat {chat_id}: {type(e).__name__} - {e}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    # 3. Finalize: Save assistant message to Database
    async with SessionLocal() as session:
        message_repo = MessageRepository(session)
        assistant_message = Message(
            chat_id=chat_id,
            model=requested_model,
            tokens=token_count,
            role="assistant",
            content=full_response,
            timestamp=None
        )
        await message_repo.add(assistant_message)
        await session.commit() # Commit the transaction
        
    # 4. Publish completion event
    await publish_stream_event(chat_id=chat_id, token="", is_finished=True)
    logger.info(f"Finished processing and saved assistant message for chat {chat_id}")

async def main():
    logger.info("Worker started, waiting for tasks...")
    while True:
        try:
            task = await dequeue_task(timeout=3)  
            
            if task:
                try:
                    await process_task(task)
                except Exception as e:
                    logger.error(f"Task failed for chat {task.get('chat_id')}: {e}. Moving to DLQ.")
                    # Move to Dead Letter Queue with the error message attached
                    task["error"] = str(e)
                    await redis_client.rpush(DLQ_NAME, json.dumps(task))
                    
        except Exception as e:
            logger.error(f"Critical Queue Error: {e}")
            await asyncio.sleep(5)  

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker gracefully shutting down.")