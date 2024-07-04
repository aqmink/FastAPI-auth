from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi import FastAPI
import uvicorn

from auth import auth_router

app = FastAPI()

app.include_router(auth_router.router)

# app.add_middleware(HTTPSRedirectMiddleware)

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*",],
)


@app.get('/root')
async def root():
    return {"message": "Hello, world!"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
