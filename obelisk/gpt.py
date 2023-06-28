"""
uses ChatGPT API to generate a response to a prompt.
some built in throttling so I don't become broke.
"""

from datetime import datetime, timedelta
import os
import sys
from typing import Optional

from aiohttp import ClientSession
from astral.sun import sun
from astral import LocationInfo

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

    def reset(self):
        self.prompt = 0
        self.completion = 0

    async def _maybe_reset(self):
        if self.next_reset_dt is None or datetime.utcnow() > self.next_reset_dt:
            if self.next_reset_dt is not None:
                logger.debug('the sun has set again...')
            self.reset()
            # Calculate the next reset time based on the current time
            self.next_reset_dt = self.get_next_reset_time()

    def get_next_reset_time(self) -> datetime:
        # 51.178852, -1.826176
        location = LocationInfo(
            latitude=-51.178889,  # Latitude of stonehenge antipode
            longitude=179.826176,  # Longitude of stonehenge antipode
        )

        # Get today's sunset time at stonehenge antipode
        s = sun(location.observer, date=datetime.utcnow())
        sunset = s["sunset"].replace(tzinfo=None)
        if sunset < datetime.utcnow():
            # if sunset is before now, then it's already set and we need to
            # set it to tomorrow
            s = sun(location.observer, date=datetime.utcnow() + timedelta(days=1))
            sunset = s["sunset"].replace(tzinfo=None)

        return sunset

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
