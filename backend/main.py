from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="Wood Cutting Optimizer API",
    description="AutoCUT-style cutting optimization for wood boards",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api", tags=["cutting"])


@app.get("/")
async def root():
    return {
        "message": "Wood Cutting Optimizer API",
        "version": "1.0.0",
        "endpoints": {
            "calculate": "/api/calculate",
            "calculate_report": "/api/calculate/report"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
