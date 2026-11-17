"""FastAPI & ADK HTTP Service for Cloud Run and Agent Runtime deployment."""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.main_agent import coordinator_service

app = FastAPI(
    title="First Milestones — Early Intervention Triage Agent API",
    description="ADK-powered Early Intervention and Network-Audit Assistant for Mississippi IDEA Part C.",
    version="1.0.0",
)


class BriefRequest(BaseModel):
    child_age_months: int = 22
    home_tract_geoid: str = "28133950100"
    primary_language: str = "Spanish"
    medicaid_enrolled: bool = True
    family_name: str = "Ramirez"
    child_name: str = "Mateo"


@app.get("/health")
def health_check():
    """Liveness & readiness probe."""
    return {"status": "healthy", "service": "first-milestones-ei-agent", "state": "MS"}


@app.post("/api/brief")
def generate_brief(req: BriefRequest):
    """Generates the official 45-Day Pathway & Bottleneck Brief."""
    try:
        return coordinator_service.generate_45_day_brief(
            child_age_months=req.child_age_months,
            home_tract_geoid=req.home_tract_geoid,
            primary_language=req.primary_language,
            medicaid_enrolled=req.medicaid_enrolled,
            family_name=req.family_name,
            child_name=req.child_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("agent.server:app", host="0.0.0.0", port=port, reload=False)
