from contextlib import asynccontextmanager

from fastapi import FastAPI

from .configure import configure
from .core import openapi
from .endpoints import router
from .middleware import middleware
from .settings import DEBUG_MODE, URL_PREFIX

configure()


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


app = FastAPI(
    debug=DEBUG_MODE,
    middleware=middleware,
    lifespan=lifespan,
    openapi_url='{}/openapi.json'.format(URL_PREFIX),
    docs_url='{}/docs'.format(URL_PREFIX),
)

app.include_router(router, prefix=URL_PREFIX)

app.openapi = openapi.__get__(app, type(app))
