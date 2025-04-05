import json
import os
import requests
import streamlit as st
from crewai.tools import BaseTool
from pydantic import BaseModel,Field
from unstructured.partition.html import partition_html
from crewai import Agent,Task,Process,Crew
from crewai import LLM
from dotenv import load_dotenv

load_dotenv()
brow_api=os.getenv("BROWSERLESS_API_KEY")

class WebsiteInput(BaseModel):
    website: str = Field(...,description="The URL of the website need to scrap")
    
    
class BrowserTools(BaseTool):
    name: str ="Scrap website content"
    description: str = "Useful to scrap and summerize the website cintent"
    agr_schema: type[BaseModel] = WebsiteInput
    
    def _run(self,website:str) -> str:
        try:
            url = f"https://chrome.browserless.io/content?token={brow_api}"
            payload =  json.dumps({"url": website})
            header={"cache-control":"no-cache","content-type":"application/json"}
            response =  requests.request("POST",url,header=header,data=payload)
            
            if response.status_code != 200:
                return f"Error: Failed to fetch the website content. Status code: {response.ststus_code}"
            
            elements=partition_html(text=response.text)
            content="\n\n".join([str[ele] for ele in elements])
            content = [content[i:i + 8000] for i in range(0, len(content), 8000)]
            summaries = []
            
            llm=LLM(
                model="gemini/gemini-2.0-flash",
                temperature=0.8
            )
            
            
            for chunk in content:
                agent=Agent(
                    role="Principal researcher and summerizer",
                    goal="do amazing researches and summeries based on the content you are working with",
                    backstory="you are an principal researcher and summerizer at a very big researcher agency and good at your task and perforn your workm with high accuracy",
                    llm=llm,
                    allow_delegation=False
                )
                task=Task(
                    name="summerize the content",
                    description=f"Analyze and summerize the conetent given, make sure to summerize by maintaining the mkist relevant information in the summery, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}",
                    agent=agent
                )
                summary=task.execute()
                summaries.append(summary)
                
            return "\n\n".join(summaries)
        
        except Exception as e:
            return f"Error: {str(e)}"
    async def _arun(self, website: str) -> str:
        raise NotImplementedError("Async not implemented")