from crewai import Agent,Task,Process,Crew,LLM
from trip_agents import TripAgents,StreamToExpander
from trip_tasks import TripTasks
import streamlit as st
import datetime
import sys


st.set_page_config(page_icon="✈️",page_title="Trip_planner_agent",layout="wide")

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


class TripCrew:
    
    def __init__(self,origin,cities,date_range,interests):
        self.origin=origin
        self.cities=cities
        self.date_range=f"{date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}"
        self.interests=interests
        self.output_placeholder=st.empty()
        self.llm=LLM(model="gemini/gemini-2.0-flash")
        
        
        
    def run(self):
        try:
            agents=TripAgents(self.llm)
            tasks=TripTasks()
            city_selector_agent=agents.city_selection_agent()
            local_expert_agent=agents.local_expert()
            travel_planner=agents.travel_planner()
            identify_task=tasks.identify_task(city_selector_agent,self.origin,self.cities,
                                              self.interests,self.date_range)
            gather_task=tasks.gather_task(local_expert_agent,self.origin,self.interests,self.date_range)
            travel_plan_task=tasks.plan_task(travel_planner,self.origin,self.interests,self.date_range)
            
            crew=Crew(
                agents=[city_selector_agent,local_expert_agent,travel_planner],
                tasks=[identify_task,gather_task,travel_plan_task],
                verbose=True
            )
            
            result=crew.kickoff()
            self.output_placeholder.markdown(result)
            return result
        except Exception as e:
            st.error(f"An Error occured: {str(e)}")
            return None
        
        
        
if __name__ == "__main__":
    icon("🏖️ VacAIgent")
    st.subheader("Let AI Agents Plan Your Next Vacation!",divider="rainbow",anchor=False)
    today=datetime.datetime.now()
    apr=datetime.date(today.year,4,20)
    
    
    
    with st.sidebar:
        st.header("👇 Enter your trip details")
        with st.form("my_form"):
            origin=st.text_input("Where are you located?",placeholder="Enter your current location")
            cities=st.text_input("Where you want to travel?",placeholder="Bali,Paris,Manali")
            date_range=st.date_input(
                "Date range you are interested in traveling?",
                min_value=today,
                value=(today,apr+datetime.timedelta(days=9)),
                format="YYYY/MM/DD"
                
                
            )
            interests=st.text_area("What are your Interests?",placeholder="Swiming,Adventure,Hiking,Eating,snow Expedition")
            submitted=st.form_submit_button("Submit")
        st.divider()
        st.sidebar.markdown(
        """
        Credits to [**@joaomdmoura**](https://twitter.com/joaomdmoura)
        for creating **crewAI** 🚀
        """,
            unsafe_allow_html=True
        )
        st.sidebar.info("Click the logo to visit GitHub repo", icon="👇")
        st.sidebar.markdown(
            """
        <a href="https://github.com/joaomdmoura/crewAI" target="_blank">
            <img src="https://raw.githubusercontent.com/joaomdmoura/crewAI/main/docs/crewai_logo.png" alt="CrewAI Logo" style="width:100px;"/>
        </a>
        """,
            unsafe_allow_html=True
        )
        
        
        
        
        

if submitted:
    with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
        with st.container(height=500, border=False):
            sys.stdout = StreamToExpander(st)
            trip_crew = TripCrew(origin, cities, date_range, interests)
            result = trip_crew.run()
        status.update(label="✅ Trip Plan Ready!",
                      state="complete", expanded=False)
    st.subheader("Here is the Grip plan for you!",anchor=False,divider="rainbow")
    st.markdown(result)
            
            
            