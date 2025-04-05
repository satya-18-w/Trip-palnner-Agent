from crewai.tools import BaseTool
from pydantic import BaseModel,Field

# I am trying to create a custom calculator tool for the crewai framework.

class CalculationInput(BaseModel):
    operation: str = Field(...,description="The mathematical expression to evaluate eg: 2+3 or 2*7 or 2/3 or 3-8 etc.")
    
    
class CalculatorTools(BaseTool):
    name: str = "Make a calculation"
    description: str ="Useful to perform mathematical operations and calculations.like sum,minus,multiplication,division etc."
    args_schema: type[BaseModel] = CalculationInput
    
    
    def _run(self,operation: str) -> float:
        return eval(operation)
    async def _arun(self,operation: str) -> float:
        raise NotImplementedError("Async not implemented")