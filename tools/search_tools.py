import json
import requests
import streamlit as st
from crewai.tools import BaseTool
from pydantic import BaseModel,Field
import os
from dotenv import load_dotenv

load_dotenv()
serp_api=os.getenv("SERPER_API_KEY")

class SearchQuery(BaseModel):
    query: str =Field(...,description="The seaerch query to search for")
    
class SearchTools(BaseTool):
    name: str= "Search the web"
    description: str = "useful to search over the internet and get the relevant information in a structured manner and return result"
    args_schema: type[BaseModel] = SearchQuery
    
    def _run(self,query: str) -> str:
        try:
            top_results_to_return  = 5
            url = "https://google.serper.dev/search"
            payload = json.dumps({
            "q": query
            })
            headers=  {
            'X-API-KEY': serp_api,
            'Content-Type': 'application/json'
            }
            response=requests.request("POST",url,headers=headers,data=payload)
            
            if response.ststus_code != 200:
                return f"Error: Search API request failed. Status code: {response.status_code}"
            data=response.json()
            if 'organic' not in data:
                return "No results found or API error occurred."
            
            results=data["organic"]
            
            string=[]
            for  result in results[:top_results_to_return]:
                title=result["title"]
                link=result["link"]
                snippet=result["snippet"]
                string.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n\n")
                return "\n".join(string) if string else "No valid result found"
            
        except Exception as e:
            raise ValueError(f"Ann error occured : {e}")
        
    async def _arun(self, query: str) -> str:
        raise NotImplementedError("Async not implemented")