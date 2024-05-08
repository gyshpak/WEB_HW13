import os
import uvicorn

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.database.db import get_db
from src.routes import contacts
from src.routes import auth

# from my_limiter import lifespan
from conf.config import config

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


# app = FastAPI(lifespan=lifespan)
app = FastAPI()

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    """
    The index function is the default function that will be called when a user
    visits the root of your API. It returns a simple message to let users know
    that they have successfully connected to your API.
    
    :return: A dictionary
    :doc-author: Trelent
    """
    return {"message": "Hello World"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks if the database connection is working.
    It does this by executing a simple SQL query and checking if it returns any results.
    If it doesn't, then we know something's wrong with the database connection.
    
    :param db: AsyncSession: Inject the database session into the function
    :return: A dict
    :doc-author: Trelent
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == "__main__":
    # uvicorn.run("main:app", host="localhost", port=8000, reload=True)
    # uvicorn.run("main:app", host="0,0,0,0", port=int(os.environ.get("PORT", 8000)))
    uvicorn.run("main:app", host="0,0,0,0", port=8000, reload=True, log_level="info")
