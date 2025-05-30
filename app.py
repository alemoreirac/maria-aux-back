import logging
from controllers import ai_controller, user_controller, prompt_controller, parameter_controller, menu_controller,report_controller,favourite_prompt_controller
from database.db_setup import DatabaseSetup
from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware 
import uvicorn
import os
from dotenv import load_dotenv
load_dotenv()

docs_url = None if os.getenv("ENV") == "prod" else "/docs"

app = FastAPI(
    title="Maria-Aux Back-end",
    description="API Maria Aux 1.0.0",
    docs_url=docs_url
)

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
origins = [
    "https://maria-aux-front-production.up.railway.app", 
]

# Add CORS middleware to your FastAPI application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # List of allowed origins
    allow_credentials=True, # Allow cookies to be included in cross-origin requests
    allow_methods=["*"], # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allow all headers
)


app.include_router(parameter_controller.router)
app.include_router(ai_controller.router)
app.include_router(prompt_controller.router)
app.include_router(user_controller.router)
app.include_router(menu_controller.router)
app.include_router(report_controller.router)
app.include_router(favourite_prompt_controller.router)

@app.get("/")
async def read_root(): 
    return {"message": "Maria Auxiliadora API está ok!"}

if __name__ == "__main__":
    db_setup = DatabaseSetup()
    success = db_setup.setup_database()
    if success:
        print("Database was setup successfully")
    else:
        print("Database setup failed")
    uvicorn.run(app, host="0.0.0.0", port=7860)

