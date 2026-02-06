from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import create_db_and_tables
from .products.api.category import router as category_router
from .products.api.product import router as products_router
from .products.api.product_group import router as product_group_router
from .products.api.product_image import router as product_image_router
from .products.api.variation import router as variation_router
from .products.api.variation_option import router as variation_options_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://webbfarstun.shop",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(products_router)
app.include_router(category_router)
app.include_router(product_group_router)
app.include_router(variation_router)
app.include_router(variation_options_router)
app.include_router(product_image_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/goodbye")
def read_root():
    return {"Goodbye": "World"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
