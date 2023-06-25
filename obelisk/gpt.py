"""
uses ChatGPT API to generate a response to a prompt
"""

import os
from typing import Optional

from aiohttp import ClientSession

from obelisk.logger import logger

API_KEY = os.environ.get('OPENAI_API_KEY')
if not API_KEY or not API_KEY.startswith('sk-'):
    logger.warning("OPENAI_API_KEY not set or incorrect, some functionality is disabled")


class MissingOpenAIKeyError(Exception):
    pass


async def get_response(session: ClientSession,
                        prompt: str,
                        system_prompt: Optional[str]=None,
                        retries: int=5,
                        raise_on_error: bool=False) -> str:
    endpoint_url = "https://api.openai.com/v1/chat/completions"
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload: dict = {"model": 'gpt-3.5-turbo', "messages": [{"role": "user", "content": prompt}]}
    if system_prompt:
        payload['messages'].insert(0, {"role": "system", "content": system_prompt})
    retry = 0
    while retry < retries:
        async with session.post(endpoint_url, headers=headers, json=payload) as response:
            data = await response.json()
            if 'error' in data:
                logger.warning(f"error in response, retrying... {data['error']}")
                retry += 1
                continue
            return data['choices'][0]['message']['content']
    if raise_on_error:
        raise RuntimeError(f"error in response, retries exhausted: {data['error']}")
    else:
        return {'error': f'too many retries, getting: {data["error"]}'}
