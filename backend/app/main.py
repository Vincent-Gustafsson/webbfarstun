from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from .db import create_db_and_tables
from .products.api.action import router as action_router
from .products.api.category import router as category_router
from .products.api.product import router as products_router
from .products.api.product_group import router as product_group_router
from .products.api.product_image import router as product_image_router
from .products.api.review import product_reviews_router
from .products.api.review import router as review_router
from .products.api.shopping_cart import router as shopping_cart_router
from .products.api.shopping_cart_item import router as shopping_cart_item_router
from .products.api.user import router as user_router
from .products.api.variation import router as variation_router
from .products.api.variation_option import router as variation_options_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    root_path="/api",
    docs_url=None,
    redoc_url=None,
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://webbfarstun.shop",
    "https://dev.webbfarstun.shop",
    "http://dev.webbfarstun.shop",
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
app.include_router(user_router)
app.include_router(action_router)
app.include_router(review_router)
app.include_router(product_reviews_router)
app.include_router(shopping_cart_router)
app.include_router(shopping_cart_item_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/goodbye")
def read_root():
    return {"Goodbye": "World"}


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    openapi_url = f"{app.root_path}{app.openapi_url}"
    html = get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API Docs",
    ).body.decode("utf-8")

    custom_css = """
    <style>
      html, body { background: #f5f7fb !important; }
      .swagger-ui { color: #0f172a !important; }
      .swagger-ui .topbar { background: #0b1220 !important; }
      .swagger-ui .info .title,
      .swagger-ui .info p,
      .swagger-ui .opblock-description-wrapper p,
      .swagger-ui .opblock-summary-description,
      .swagger-ui label,
      .swagger-ui .parameter__name,
      .swagger-ui .response-col_status,
      .swagger-ui .response-col_description { color: #0f172a !important; }
      .swagger-ui .scheme-container {
        background: #ffffff !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08) !important;
      }
    </style>
    """
    return HTMLResponse(html.replace("</head>", f"{custom_css}</head>"))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
