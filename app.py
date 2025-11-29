import streamlit as st
from typing import Dict, List

class UserProfile:
    def __init__(self, budget_weekly=5000, diet_prefs=["vegetarian"], family_size=2):
        self.budget_weekly = budget_weekly
        self.diet_prefs = diet_prefs
        self.family_size = family_size

class MealPlan:
    def __init__(self, meals: Dict, total_cost: float):
        self.meals = meals
        self.total_cost = total_cost
    
    def display(self):
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        output = "Weekly Plan (Rs" + str(int(self.total_cost)) + "):\n"
        for i, day in enumerate(days):
            meal = self.meals.get("day" + str(i+1), "Rest Day")
            output += "  " + day + ": " + meal + "\n"
        return output

class ShoppingList:
    def __init__(self, items: List, total: float):
        self.items = items
        self.total = total

class FinanceTools:
    def get_user_budget(self, user_id: str) -> float: 
        return 5000
    
    def search_recipes(self, diet_prefs: List[str], budget: float, servings=2) -> List[Dict]:
        return [
            {"name": "Dal Tadka + Roti", "cost": 60},
            {"name": "Veg Stir Fry + Quinoa", "cost": 75},
            {"name": "Paneer Tikka + Salad", "cost": 90},
            {"name": "Moong Dal Khichdi", "cost": 45},
            {"name": "Veg Biryani + Raita", "cost": 80},
            {"name": "Aloo Gobi + Chapati", "cost": 55},
            {"name": "Rajma + Rice", "cost": 65}
        ]
    
    def generate_shopping_list(self, meals: Dict) -> ShoppingList:
        return ShoppingList([
            "2kg Rice (Rs120)", "1kg Dal (Rs150)", "500g Paneer (Rs250)", 
            "Veggies 2kg (Rs100)", "Spices (Rs80)", "2L Milk (Rs100)"
        ], 2800)

tools = FinanceTools()

class ClassifierAgent:
    def classify_intent(self, message: str) -> str:
        msg = message.lower()
        if any(w in msg for w in ['budget', 'money', 'rs', 'remaining']): 
            return "budget_check"
        elif any(w in msg for w in ['shopping', 'list', 'grocery']): 
            return "shopping_list"
        elif any(w in msg for w in ['meal', 'plan', 'vegetarian', 'food']): 
            return "meal_planning"
        return "general"

classifier = ClassifierAgent()

class InMemorySessionService:
    def __init__(self): 
        self.sessions = {}
    
    def get_session(self, user_id: str) -> Dict:
        if user_id not in self.sessions:
            self.sessions[user_id] = {"profile": UserProfile(), "current_plan": None}
        return self.sessions[user_id]

session_service = InMemorySessionService()

class BudgetBiteAgent:
    def __init__(self):
        self.session_service = session_service
        self.classifier = classifier
        self.tools = tools
    
    def process_query(self, user_id: str, message: str) -> str:
        session = self.session_service.get_session(user_id)
        intent = self.classifier.classify_intent(message)
        
        if intent == "meal_planning":
            profile = session["profile"]
            recipes = self.tools.search_recipes(profile.diet_prefs, profile.budget_weekly)
            meals = {"day" + str(i+1): recipes[i % len(recipes)]["name"] for i in range(7)}
            plan = MealPlan(meals, 2800)
            session["current_plan"] = plan
            return plan.display() + "\nBudget used: Rs" + str(plan.total_cost) + "/Rs" + str(profile.budget_weekly)
        
        elif intent == "budget_check":
            budget = self.tools.get_user_budget(user_id)
            if session.get("current_plan"):
                remaining = budget - session["current_plan"].total_cost
                return "Weekly budget: Rs" + str(int(budget)) + "\nRemaining: Rs" + str(int(remaining))
            return "Weekly budget: Rs" + str(int(budget))
        
        elif intent == "shopping_list":
            shopping = self.tools.generate_shopping_list({})
            return "Shopping List (Rs" + str(int(shopping.total)) + "):\n" + "\n".join(shopping.items)
        
        return """BudgetBite - Smart Meal Planner

Quick Actions:
• "Create my weekly vegetarian meal plan" 
• "What's my budget remaining?"
• "Generate shopping list"

Budget: Rs5,000/week"""

agent = BudgetBiteAgent()

st.set_page_config(page_title="BudgetBite", page_icon="🤖", layout="wide")
st.title("🤖 BudgetBite - AI Meal Planner")
st.markdown("---")

with st.sidebar:
    st.header("👤 Profile")
    budget_input = st.number_input("Budget Rs", 1000, 20000, 5000)

if "messages" not in st.session_state:
    st.session_state.messages = []

col1, col2, col3 = st.columns(3)
if col1.button("📅 Meal Plan"): 
    st.session_state.messages.append({"role": "user", "content": "Create meal plan"})
    st.rerun()
if col2.button("💰 Budget"): 
    st.session_state.messages.append({"role": "user", "content": "budget?"})
    st.rerun()
if col3.button("🛒 Shopping"): 
    st.session_state.messages.append({"role": "user", "content": "shopping list"})
    st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about meals, budget, shopping..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        response = agent.process_query("user", prompt)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
