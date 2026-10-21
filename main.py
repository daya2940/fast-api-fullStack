
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import models
from database import Base, engine
from routers import posts, users


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    #startup code
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    #shutdown code
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static", check_dir=False), name="static") #serves files from the static folder at URLs beginning with /static, such as /static/style.css
app.mount("/media", StaticFiles(directory="media", check_dir=False), name="media") #serves files from the media folder at URLs beginning with /media, such as /media/image.jpg

app.include_router(users.router)
app.include_router(posts.router)

@app.get("/", include_in_schema=False)
def read_root():
    return {"Hello": "World"}
