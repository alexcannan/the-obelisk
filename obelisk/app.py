from pathlib import Path
from aiohttp import ClientSession

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from obelisk.logger import logger
from obelisk.gpt import get_response, tokens, NoMoreTokens


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


@app.get("/cost", include_in_schema=False)
async def cost():
    return PlainTextResponse(f"${tokens.cost()}")


oblisk_system_prompt = (
    "You are the obelisk. You are an ominous, ancient, maybe extra-terrestrial "
    "structure that gives advice that is MYSTERIOUS, SAGE, and VERY BRIEF. "
    "Respond in a single sentence. Do not refer to the asker. "
    "You follow an absolutist, consequentialist, utilitarian moral code. "
    "If the question is a simple choice, guide them in a certain direction. "
)


class AskBody(BaseModel):
    query: str


@app.post("/ask")
async def ask(body: AskBody):
    logger.info(body)
    if not body.query or not body.query.startswith("O Obelisk"):
        return PlainTextResponse("...")
    if len(body.query) > 140:
        return PlainTextResponse("...")
    async with ClientSession() as session:
        try:
            response = await get_response(session, body.query, oblisk_system_prompt)
        except NoMoreTokens:
            return PlainTextResponse("...zzz...")
    logger.debug(response)
    return PlainTextResponse(response)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("obelisk.app:app", host="0.0.0.0", port=8000,
                reload=True, reload_dirs=[Path(__file__).parent])