from fastapi import FastAPI,HTTPException,Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from datetime import date,datetime
from typing import Optional
from crewai import Crew,Process,Agent,Task,LLM
from trip_agents import TripAgents
from trip_tasks import TripTasks
import os
from dotenv import load_dotenv
from functools import lru_cache


load_dotenv()

app=FastAPI(
    title="Trip planner agent",
    description="Ai-Powered Travel planning agent",
    version="0.0.1"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripRequest(BaseModel):
    origin : str =Field(...,example="Bhubaneswar,India",description="Your current location")
    destination : str=Field(...,example="Manali,India",description="Place you want to visit or your destination city and country")
    start_date: date = Field(...,example="2025-04-16",description="Start date of your trip")
    end_date: date = Field(...,example="2025-04-22",description="End date of your trip")
    interests: str = Field(...,example="2 adults who love swimming, dancing, hiking, shopping, local food, water sports adventures and rock climbing",description="your intrests and trip details")
    
    
    
class TripResponse(BaseModel):
    status: str
    message: str
    itinerary: Optional[str] = None
    error: Optional[str] = None
    
    
    
    
class Settings:
    def __init__(self):
        load_dotenv()
        self.GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
        self.SERPER_API_KEY=os.getenv("SERPER_API_KEY")
        self.BROWSERLESS_API_KEY=os.getenv("BROWSERLESS_API_KEY")
        
        
        
@lru_cache()
def get_settings():
    return Settings()


def validate_api_key(settings: Settings = Depends(get_settings)):
    required_key={
        "GEMINI_API_KEY":settings.GEMINI_API_KEY,
        "SERPER_API_KEY":settings.SERPER_API_KEY,
        "BROWSERLESS_API_KEY":settings.BROWSERLESS_API_KEY
    }
    
    missing_key=[key for key,value in required_key.items() if value == None]
    if missing_key:
        raise HTTPException(
            status_code=500,
            detail=f"Missing required API key: {", ".join(missing_key)}"
        )
        
    return settings



class TripCrew:
    def __init__(self,origin,destination,date_range,interests):
        self.origin=origin
        self.destination=destination
        self.date_range=date_range
        self.interests=interests
        
        self.llm=LLM(model="gemini/gemini-2.0-flash")
        
        
    def run(self):
        try:
            agents=TripAgents(llm=self.llm)
            tasks=TripTasks()
            
            city_selector_agent=agents.city_selection_agent()
            local_expert_agent=agents.local_expert()        
            travel_planner_agent=agents.travel_planner()
            identify_task = tasks.identify_task(
                city_selector_agent,
                self.origin,
                self.destination,
                self.interests,
                self.date_range
            )
            gather_task = tasks.gather_task(
                local_expert_agent,
                self.origin,
                self.interests,
                self.date_range
            )
            
            plan_task = tasks.plan_task(
                travel_planner_agent,
                self.origin,
                self.interests,
                self.date_range
            )
            
            
            crew=Crew(
                agents=[city_selector_agent,local_expert_agent,travel_planner_agent],
                tasks=[identify_task,gather_task,plan_task],
                verbose=True
            )
            
            result=crew.kickoff()
            
            return result.raw if hasattr(result, 'raw') else str(result)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
            
            
            
# APi building

@app.get("/")
async def root():
    return {
        "message":" Welcome to the travel planner Api",
        "docs_url":"/docs",
        "redoc_url":"/redoc"
    }
    
    
@app.post("/api/v1/plan-trip",response_model=TripResponse)
async def plan_trip(trip_request: TripRequest,settings: Settings = Depends(validate_api_key)):
    
            if trip_request.end_date < trip_request.start_date:
                raise HTTPException(
                    status_code=400,
                    detail="End date must be after start date"
                )
                
            # Format date range
            date_range = f"{trip_request.start_date} to {trip_request.end_date}"
            
            try:
                trip_crew=TripCrew(
                    origin=trip_request.origin,
                    destination=trip_request.destination,
                    date_range=date_range,
                    interests=trip_request.interests
                )
                
                itinerary=trip_crew.run()
                
                if not isinstance(itinerary,str):
                    itinerary=str(itinerary)
                    
                return TripResponse(
                    status="success",
                    message="Trip planned Successfully",
                    itinerary=itinerary
                )
                
            except Exception as e:
                return TripResponse(
                status="error",
                message="Failed to generate trip plan me satya",
                error=str(e)
                )
                
                
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=5000)
            