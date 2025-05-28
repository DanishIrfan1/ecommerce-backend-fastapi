"""
Main entry point for the application.

This simply imports and runs the FastAPI app from the app package.
"""

from app.main import app

# This will allow running the application with `python main.py`
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
