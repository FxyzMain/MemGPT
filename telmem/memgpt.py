import requests
import json
from config import MEMGPT_ADMIN_API_KEY
from db import save_user_api_key, save_user_agent_id, get_user_api_key, get_user_agent_id

async def create_memgpt_user(telegram_user_id: int):
    response = requests.post('http://localhost:8283/admin/users', headers={'Authorization': f'Bearer {MEMGPT_ADMIN_API_KEY}'})
    if response.status_code == 200:
        user_data = response.json()
        user_api_key = user_data['api_key']
        await save_user_api_key(telegram_user_id, user_api_key)
        agent_response = requests.post(
            'http://localhost:8283/api/agents',
            headers={'Authorization': f'Bearer {user_api_key}', 'Content-Type': 'application/json'},
            data=json.dumps({
                "config": {
                    "name": f"AgentForTelegramUser{telegram_user_id}",
                    "preset": "memgpt_chat",
                }
            })
        )
        if agent_response.status_code == 200:
            agent_data = agent_response.json()
            agent_id = agent_data['agent_state']['id']
            await save_user_agent_id(telegram_user_id, agent_id)
            return "Your MemGPT agent has been created."
        else:
            return "Failed to create MemGPT agent."
    else:
        return "Failed to create MemGPT user."

async def send_message_to_memgpt(telegram_user_id: int, message_text: str):
    user_api_key = await get_user_api_key(telegram_user_id)
    agent_id = await get_user_agent_id(telegram_user_id)
    if not user_api_key or not agent_id:
        return "No API key or agent found. Please start again."
    response = requests.post(
        'http://localhost:8283/api/agents/message',
        headers={'Authorization': f'Bearer {user_api_key}'},
        json={'agent_id': agent_id, 'message': message_text, 'stream': True, 'role': 'user'}
    )
    if response.status_code == 200:
        memgpt_response = response.json().get('response')
        return memgpt_response
    else:
        return "Failed to send message to MemGPT."
