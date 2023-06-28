"""
uses ChatGPT API to generate a response to a prompt.
some built in throttling so I don't become broke.
"""

from datetime import datetime, timedelta
import os
import sys
from typing import Optional

from aiohttp import ClientSession
from dateutil.parser import parse

from obelisk.logger import logger

API_KEY = os.environ.get('OPENAI_API_KEY')
if not API_KEY or not API_KEY.startswith('sk-'):
    logger.error("OPENAI_API_KEY not set or incorrect, exiting...")
    sys.exit(1)


DAILY_COST_LIMIT_DOLLARS = float(os.environ.get('DAILY_COST_LIMIT', 1))


class NoMoreTokens(Exception):
    pass


class TokensUsed():
    """
    tracks token usage, resets at sunset at stonehenge antipode
    """
    prompt: int = 0
    completion: int = 0
    next_reset_dt: Optional[datetime] = None

    async def log_usage(self, usage: dict):
        await self._maybe_reset()
        self.prompt += usage['prompt_tokens']
        self.completion += usage['completion_tokens']

    async def set_next_reset_(self):
        # fill next_reset_dt if it's not already filled
        if not self.next_reset_dt:
            async with ClientSession() as session:
                while not self.next_reset_dt or self.next_reset_dt < datetime.utcnow():
                    dtdiff = 0
                    params = {"lat": -39.178844,
                                "lng": 179.826183,
                                "date": (datetime.utcnow()+timedelta(days=dtdiff)).strftime('%Y-%m-%d'),
                                "formatted": 0}
                    async with session.get("https://api.sunrise-sunset.org/json",
                                           params=params) as resp:
                        data = await resp.json()
                    self.next_reset_dt = parse(data['results']['sunset']).replace(tzinfo=None)
                    dtdiff += 1
            logger.debug(f"next reset at {self.next_reset_dt}")

    async def _maybe_reset(self):
        # reset values every time the sun sets at the stonehenge antipode
        # https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400&date=2023-06-10
        # but use -39.178844, 179.826183
        await self.set_next_reset_()
        if self.next_reset_dt < datetime.utcnow():
            logger.info("the obelisk has reset")
            self.reset()
            self.next_reset_dt = None

    def reset(self):
        self.prompt = 0
        self.completion = 0

    def cost(self) -> float:
        """ returns total spent on requests in dollars """
        # prompt: $0.0015 / 1K tokens
        # completion: $0.002 / 1K tokens
        return self.prompt * 0.0015 / 1000 + self.completion * 0.002 / 1000


tokens = TokensUsed()


async def get_response(session: ClientSession,
                        prompt: str,
                        system_prompt: Optional[str]=None,
                        retries: int=5,
                        raise_on_error: bool=False) -> str:
    if tokens.cost() > DAILY_COST_LIMIT_DOLLARS:
        raise NoMoreTokens("no more tokens")
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
            # 'usage': {'prompt_tokens': 85, 'completion_tokens': 17, 'total_tokens': 102}
            await tokens.log_usage(data['usage'])
            return data['choices'][0]['message']['content']
    if raise_on_error:
        raise RuntimeError(f"error in response, retries exhausted: {data['error']}")
    else:
        return {'error': f'too many retries, getting: {data["error"]}'}
