from crewai import Agent
import re
import streamlit as st
from langchain_core.language_models.chat_models import BaseChatModel
from tools.browser_tools import BrowserTools
from tools.search_tools import SearchTools
from tools.claculator_tools import CalculatorTools


class TripAgents:
    def __init__(self, llm: BaseChatModel = None):
        if llm is None:
            self.llm=LLM(model="gemini/gemini-2.0-flash",temperature=0.8)
            
        else:
            self.llm=llm
            
        # Initialize the tools
        self.search_tools=SearchTools()
        self.calculator_tools=CalculatorTools()
        self.browser_tools=BrowserTools()
        
    def city_selection_agent(self):
        return Agent(
            role="City selection Expert ",
            goal="Select the best city for enjoyment according to the weather,season and budget.",
            backstory="You are a travel agent who is expert in selectiing the best city according to the travel data pick the ideal destinatioons",
            llm=self.llm,
            tools=[self.search_tools,self.browser_tools],
            allow_delegation=False,
            verbose=True
        )
        
    def local_expert(self):
        return Agent(
            role="Local Expert of the selected city",
            goal="provide the best local destinations , activities and best insides of the selected city",
            backstory="You are a local guide who have experities in the selected city with complete touristic attractions information of the selected city",
            verbose=True,
            llm=self.llm,
            tools=[self.search_tools,self.browser_tools],
            allow_delegation=False,
            
        )
        
        
    def travel_planner(self):
        return Agent(
            role="Amazing Travel Planner",
            goal="create the travel plan day by day with in the selected city with budget constraints according to the weather conditions",
            backstory="You are a travel planner who is experties in travel planning and logistics with decades of experience",
            verbose=True,
            llm=self.llm,
            tools=[self.browser_tools,self.search_tools,self.calculator_tools],
            allow_delegation=False,
            max_iterations=5,
        )
        
        
        
    
###########################################################################################
# Print agent process to Streamlit app container                                          #
# This portion of the code is adapted from @AbubakrChan; thank you!                       #
# https://github.com/AbubakrChan/crewai-UI-business-product-launch/blob/main/main.py#L210 #
###########################################################################################
class StreamToExpander:
    def __init__(self,expander):
        self.expander=expander
        self.buffer=[]
        self.colors=["red","green","blue","orange"]
        self.color_index=0
        
        
    def write(self,data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)
            
        # Check if the text contains the specified phrase and apply color
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            self.color_index = (self.color_index + 1) % len(self.colors)
            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", 
                                              f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")

        if "City Selection Expert" in cleaned_data:
            cleaned_data = cleaned_data.replace("City Selection Expert", 
                                              f":{self.colors[self.color_index]}[City Selection Expert]")
        if "Local Expert at this city" in cleaned_data:
            cleaned_data = cleaned_data.replace("Local Expert at this city", 
                                              f":{self.colors[self.color_index]}[Local Expert at this city]")
        if "Amazing Travel Concierge" in cleaned_data:
            cleaned_data = cleaned_data.replace("Amazing Travel Concierge", 
                                              f":{self.colors[self.color_index]}[Amazing Travel Concierge]")
        if "Finished chain." in cleaned_data:
            cleaned_data = cleaned_data.replace("Finished chain.", 
                                              f":{self.colors[self.color_index]}[Finished chain.]")

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []
            
            
    def flush(self):
        """Flush the buffer to the expander"""
        if self.buffer:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []

    def close(self):
        """Close the stream"""
        self.flush()