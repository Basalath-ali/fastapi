from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Ali Fast API")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Ali Fast API</title>
        </head>
        <body>
            <h1>Ali Fast API</h1>
            <p>Welcome to Ali's FastAPI application</p>
        </body>
    </html>
    """

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
