from pydantic import BaseModel, Field
from typing import List, Optional

class CategoryScore(BaseModel):
    score: int = Field(..., description="Score from 0-100", ge=0, le=100)
    assessment: str = Field(..., description="Brief assessment of the category")
    gaps: Optional[str] = Field(None, description="Identified gaps in compliance")

class EnvironmentalData(CategoryScore):
    pass

class SocialData(CategoryScore):
    pass

class GovernanceData(CategoryScore):
    pass

class ESGReport(BaseModel):
    company_name: str = Field(..., description="Name of the company")
    url: str = Field(..., description="Source URL")
    summary: str = Field(..., description="Executive summary of ESG performance")
    environmental: EnvironmentalData
    social: SocialData
    governance: GovernanceData
    timestamp: str = Field(..., description="ISO timestamp of extraction")
