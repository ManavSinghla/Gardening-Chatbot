# gardening_assistant.py
import streamlit as st
import requests
import json

# Configuration
ORS_API_KEY = st.secrets["ORS_API_KEY"]
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "http://localhost:8501",  # Update with your deployment URL
    "X-Title": "Gardening Assistant",
}

def get_coordinates(address):
    """Get coordinates using OpenRouteService API"""
    try:
        response = requests.get(
            "https://api.openrouteservice.org/geocode/search",
            headers={"Authorization": ORS_API_KEY},
            params={"text": address, "size": 1},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data["features"]:
                lon, lat = data["features"][0]["geometry"]["coordinates"]
                return lat, lon
        return None, None
    except Exception as e:
        st.error(f"🌍 Location Error: {str(e)}")
        return None, None

def get_hardiness_zone(lat, lon):
    """Mock function for hardiness zone (replace with actual API)"""
    return "8b"  # Example value

def get_gardening_response(messages):
    """Get response from OpenRouter.ai API"""
    try:
        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(OPENROUTER_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# Initialize chat
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm your Gardening Assistant. 🌱 How can I help with your plants today?"
    }]

# App Interface
st.title("🌻 Smart Gardening Assistant")
st.caption("Your AI-powered gardening expert")

# Sidebar for location input
with st.sidebar:
    st.header("📍 Location Settings")
    address = st.text_input("Enter your garden location (optional):")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process user input
if prompt := st.chat_input("Ask your gardening question..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get location context
    location_context = ""
    if address:
        lat, lon = get_coordinates(address)
        if lat and lon:
            zone = get_hardiness_zone(lat, lon)
            location_context = f"\n\n[Location: {address} | Hardiness Zone: {zone}]"
    
    # Create system message
    system_message = {
        "role": "system",
        "content": f"""You are an expert gardening assistant. Provide:
        - Plant care advice
        - Pest/disease solutions
        - Seasonal gardening tips
        - Soil management recommendations
        {location_context}"""
    }
    
    # Prepare messages for API
    messages = [system_message] + st.session_state.messages[-5:]
    
    # Generate response
    with st.spinner("🌱 Growing answers..."):
        ai_response = get_gardening_response(messages)
    
    # Add response to history
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # Rerun to display new messages
    st.rerun()