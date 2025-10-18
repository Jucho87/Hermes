from fastapi import FastAPI
from .database import engine
from .models import models
from .api import master, shopping_list, transactions, reports

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hermes API",
    description="API for shopping and market control (SACI Project).",
    version="0.1.0",
)

app.include_router(master.router, tags=["Master Data"])
app.include_router(shopping_list.router, tags=["Shopping List"])
app.include_router(transactions.router, tags=["Transactions"])
app.include_router(reports.router, tags=["Reports"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Hermes API"}