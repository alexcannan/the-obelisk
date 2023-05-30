from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from pydantic import BaseModel

from obelisk.logger import logger


app = FastAPI()


@app.get("/")
async def root():
    env = Environment(loader=FileSystemLoader(Path(__file__).parent))
    template = env.get_template('obelisk.html')
    return HTMLResponse(template.render())


@app.get("/favicon.svg", include_in_schema=False)
async def favicon():
    return FileResponse(Path(__file__).parent / "icon.svg")


class AskBody(BaseModel):
    question: str


@app.post("/ask")
async def ask(body: AskBody):
    logger.info(body)
    # TODO: actually do something with the question
    if not body.question:
        return PlainTextResponse("...")
    return PlainTextResponse("what dat mouf do")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("obelisk.app:app", host="0.0.0.0", port=8000,
                reload=True, reload_dirs=[Path(__file__).parent])