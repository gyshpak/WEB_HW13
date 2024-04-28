import uvicorn
from fastapi import FastAPI, Depends, HTTPException

from src.database.db import get_db
from src.routes import contacts
from src.routes import auth

from my_limiter import lifespan

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/api")
# app.include_router(contacts.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


@app.get("/")
def index():
    return {"message": "Hello World"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
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
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
