from pathlib import Path
import random
from aiohttp import ClientSession

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from pydantic import BaseModel

from obelisk.logger import logger
from obelisk.gpt import get_response


app = FastAPI()


@app.get("/")
async def root():
    env = Environment(loader=FileSystemLoader(Path(__file__).parent))
    template = env.get_template('obelisk.html')
    return HTMLResponse(template.render())


@app.get("/favicon.svg", include_in_schema=False)
async def favicon():
    return FileResponse(Path(__file__).parent / "icon.svg")


@app.get("/hit.mp3", include_in_schema=False)
async def hit():
    return FileResponse(Path(__file__).parent / "hit.mp3")


oblisk_system_prompt = (
    "You are the obelisk. You are an ominous, ancient structure that gives advice "
    "that is MYSTERIOUS, SAGE, and VERY BRIEF. Respond in a single sentence. "
    "You do not care about human emotions. You follow a utilitarian philosophy. "
    "If the question is a simple choice, guide them in a certain direction. "
)


class AskBody(BaseModel):
    query: str


@app.post("/ask")
async def ask(body: AskBody):
    logger.info(body)
    if not body.query or not body.query.startswith("O Obelisk"):
        return PlainTextResponse("...")
    async with ClientSession() as session:
        response = await get_response(session, body.query, oblisk_system_prompt)
    logger.debug(response)
    return PlainTextResponse(response)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("obelisk.app:app", host="0.0.0.0", port=8000,
                reload=True, reload_dirs=[Path(__file__).parent])