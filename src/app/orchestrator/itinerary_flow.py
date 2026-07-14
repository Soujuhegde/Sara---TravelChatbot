from datetime import datetime
from typing import Dict, Any
from langchain_core.messages import SystemMessage
from app.orchestrator.nlu_parser import llm
from app.config import settings

def get_itinerary_contextual_reminder(step: str, state: Dict[str, Any]) -> str | None:
    hotel_params = state.get("hotel_params") or {}
    flight_params = state.get("flight_params") or {}

    if step == "itinerary_awaiting_city":
        return "Which city or destination would you like me to plan the itinerary for?"
    elif step == "itinerary_awaiting_start_date":
        city = hotel_params.get("city") or flight_params.get("destination") or "your destination"
        return f"When are you planning to start your trip to {city}?"
    elif step == "itinerary_awaiting_days":
        return "For how many days would you like me to plan the itinerary?"
    return None

def handle_itinerary_clarification(step: str, state: Dict[str, Any]) -> Dict[str, Any]:
    msg = ""
    replies = []
    options = []
    
    hotel_params = state.get("hotel_params") or {}
    flight_params = state.get("flight_params") or {}
    selected_flight = state.get("selected_flight") or {}
    selected_hotel = state.get("selected_hotel") or {}

    if step == "itinerary_awaiting_city":
        clarification = state.get("pending_clarification")
        prefix = f"{clarification}\n\n" if clarification else ""
        msg = f"{prefix}Hi! I'm Sara, your AI travel companion. I'd love to plan a custom itinerary for you! Which city or destination are you planning to visit?"
        
    elif step == "itinerary_awaiting_start_date":
        city = hotel_params.get("city", "your destination")
        clarification = state.get("pending_clarification")
        prefix = f"{clarification}\n\n" if clarification else ""
        msg = f"{prefix}Great choice! 🌍 When are you planning to start your trip to **{city}**? (e.g. 2025-08-15 or 'next Monday')"
        replies = ["Today", "Tomorrow"]
        
    elif step == "itinerary_awaiting_days":
        days = 0
        check_in = hotel_params.get("check_in_date") or flight_params.get("departure_date")
        check_out = hotel_params.get("check_out_date")
        if check_in and check_out:
            try:
                d1 = datetime.strptime(check_in, "%Y-%m-%d")
                d2 = datetime.strptime(check_out, "%Y-%m-%d")
                days = (d2 - d1).days
            except:
                pass
                
        clarification = state.get("pending_clarification")
        prefix = f"{clarification}\n\n" if clarification else ""
        city = hotel_params.get("city") or flight_params.get("destination", "your destination")
        msg = f"{prefix}Perfect! 🗓️ How many days would you like me to plan the itinerary for **{city}**?"
        
        replies = ["3 Days", "5 Days", "7 Days"]
        if days > 0 and str(days) not in ["3", "5", "7"]:
            replies.append(f"{days} Days")
            
    elif step == "plan_itinerary":
        city = hotel_params.get("city") or flight_params.get("destination") or "your destination"
        itinerary_days = hotel_params.get("itinerary_days", 3)
        check_in = hotel_params.get("check_in_date") or flight_params.get("departure_date") or "today"
        hotel_name = selected_hotel.get("name", "")
        airline_name = selected_flight.get("airline_name", "")
        guests = hotel_params.get("guests", "1 Adult")

        itinerary_prompt = f"""You are a world-class luxury travel planner with deep expertise in {city}. 
Create an EXTREMELY DETAILED, immersive, and practical day-by-day travel itinerary.

Trip Details:
- 🌍 Destination: {city}
- 📅 Duration: {itinerary_days} days (starting {check_in})
- 🏨 Accommodation: {hotel_name if hotel_name else "To be decided"}
- ✈️ Flight: {airline_name if airline_name else "To be arranged"}
- 👥 Travellers: {guests}

STRICT OUTPUT FORMAT — Follow this EXACTLY for EVERY SINGLE DAY:

### 🌟 Day [N]: [Catchy Theme Title]
**📅 Date:** [Starting date + N-1 days]

**🌅 Morning (8:00 AM – 12:00 PM)**
- 🍳 **Breakfast:** [Specific local restaurant + must-try dish + estimated cost]
- 🗺️ [Activity 1]: [Specific location name, what to see/do, how long, entry fees if any]
- 🗺️ [Activity 2]: [Specific location name, insider tip, best time to visit]
- 🚌 **Transport:** [Specific transport mode, cost, travel time from hotel/previous spot]

**☀️ Afternoon (12:00 PM – 6:00 PM)**
- 🍽️ **Lunch:** [Specific restaurant, signature dish, price range]
- 🗺️ [Activity 3]: [Location, what makes it special, photography tips]
- 🛍️ **Shopping/Leisure:** [Market or area name, what to buy, bargaining tips]
- 🚌 **Transport:** [How to get to evening location]

**🌙 Evening (6:00 PM – 10:00 PM)**
- 🌆 [Evening activity/viewpoint/show]: [Full details, booking tips]
- 🍷 **Dinner:** [Restaurant name, cuisine type, ambiance, must-order dishes, reservation needed?]
- 🎵 **After Dinner:** [Night market/bar/cultural show suggestion if applicable]

**💡 Local Tips for Day [N]:**
- [Practical tip 1 — dress code, safety, language phrase, etc.]
- [Practical tip 2 — best photo spots, avoid tourist traps, local custom]

**💰 Estimated Daily Budget:** ₹[X,XXX] – ₹[X,XXX] per person (excluding hotel)

---

RULES YOU MUST FOLLOW:
1. Generate ALL {itinerary_days} days with FULL detail — NO shortcuts, NO "similar to previous day"
2. Name REAL, specific places, restaurants, and attractions in {city}
3. Include REALISTIC travel times and costs in local currency
4. Each day must be DISTINCT with different attractions and neighborhoods  
5. Use rich emojis throughout to make it visually engaging
6. At the very end, add a **🎒 Packing Tips** section and a **📋 Essential Info** section (visa, currency, emergency numbers, best apps to use)

Start the itinerary now with Day 1 and go all the way through Day {itinerary_days} without stopping."""

        try:
            from langchain_groq import ChatGroq
            # Use the configured model
            itinerary_llm = ChatGroq(model=settings.LLM_MODEL, temperature=0.4, max_tokens=4096)
            response = itinerary_llm.invoke([SystemMessage(content=itinerary_prompt)])
            msg = response.content
        except Exception as e:
            print(f"Itinerary LLM call failed: {e}. Falling back to default LLM.")
            try:
                if llm:
                    response = llm.invoke([SystemMessage(content=itinerary_prompt)])
                    msg = response.content
                else:
                    raise ValueError("Default LLM is not configured")
            except Exception as ex:
                print(f"Default LLM call also failed: {ex}. Using local rule-based itinerary fallback generator.")
                msg = generate_fallback_itinerary(city, itinerary_days, check_in, hotel_name, airline_name, guests)
                
        replies = ["Book a Flight", "Book a Hotel", "Plan an Itinerary"]

    return {"final_response": msg, "quick_replies": replies, "options_to_show": options}

def generate_fallback_itinerary(city: str, itinerary_days: int, check_in: str, hotel_name: str, airline_name: str, guests: str) -> str:
    from datetime import datetime, timedelta
    
    # Try to parse start date
    try:
        start_dt = datetime.strptime(check_in, "%Y-%m-%d")
    except:
        start_dt = datetime.now()
        
    lines = []
    lines.append(f"# 🗺️ Custom Itinerary for {city.upper()}")
    lines.append("")
    lines.append("Here is your detailed luxury travel plan:")
    lines.append("")
    lines.append(f"**Trip Details:**")
    lines.append(f"- 🌍 **Destination:** {city}")
    lines.append(f"- 📅 **Duration:** {itinerary_days} days")
    lines.append(f"- 🏨 **Accommodation:** {hotel_name if hotel_name else 'To be decided'}")
    lines.append(f"- ✈️ **Flight:** {airline_name if airline_name else 'To be arranged'}")
    lines.append(f"- 👥 **Travellers:** {guests}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Generic, engaging activities mapping for fallback cities
    activities_by_city = {
        "DEL": [
            ("Historical Splendors of Old Delhi", "Breakfast at Karim's (Mutton Korma & Roti, ₹350)", "Visit Red Fort (UNESCO heritage site, fee ₹35)", "Walk through Chandni Chowk spice markets", "Rickshaw ride (₹100, 15 mins)"),
            ("New Delhi Landmarks & Lutyens Zone", "South Indian Breakfast at Saravana Bhavan (₹200)", "Explore India Gate and War Memorial", "Visit Qutub Minar complex", "Metro ride to Rajiv Chowk (₹40, 20 mins)"),
            ("Cultural Temples & Spiritual Walk", "Breakfast at Wenger's (Connaught Place, ₹300)", "Visit Lotus Temple", "Explore Akshardham Temple complex", "Auto-rickshaw ride (₹120, 25 mins)"),
        ],
        "BOM": [
            ("Gateway to Mumbai Heritage Walk", "Breakfast at Café Mondegar (Keema Ghotala, ₹400)", "Visit Gateway of India", "Walk around Colaba Causeway", "Taxi ride (₹80, 10 mins)"),
            ("Coastal Drives & Sunset Promenades", "Breakfast at Yazdani Bakery (Bun Maska & Chai, ₹150)", "Visit Marine Drive", "Explore Haji Ali Dargah", "Local train ride (₹15, 20 mins)"),
            ("Artistic Passages & Ancient Caves", "Breakfast at Theobroma (Connaught Place CP or Colaba, ₹250)", "Ferry to Elephanta Caves", "Visit Jehangir Art Gallery", "Ferry ride (₹200, 1 hour)"),
        ]
    }
    
    # default activities if city is not in map
    default_activities = [
        ("Discovering Local Treasures & Museums", "Breakfast at a local café (Signature dish, ₹250)", "Visit the national museum and historical center", "Stroll through the city's botanical garden", "Walking walk (Free)"),
        ("Scenic City Panoramas & Promenades", "Breakfast at a bakery (Pastry & coffee, ₹200)", "Visit the main viewpoint or observation tower", "Stroll down the coastal/river walk", "Public bus (₹30, 15 mins)"),
        ("Spiritual Landmarks & Artisan Markets", "Breakfast at a street food market (Local specialty, ₹180)", "Visit the prominent local temple or cathedral", "Explore the cultural artisan and craft market", "Taxi (₹150, 20 mins)")
    ]
    
    city_key = city.upper()
    city_acts = activities_by_city.get(city_key, default_activities)
    
    for i in range(itinerary_days):
        day_num = i + 1
        day_date = (start_dt + timedelta(days=i)).strftime("%Y-%m-%d")
        theme, b_fast, act1, act2, trans = city_acts[i % len(city_acts)]
        
        lines.append(f"### 🌟 Day {day_num}: {theme}")
        lines.append(f"**📅 Date:** {day_date}")
        lines.append("")
        lines.append(f"**🌅 Morning (8:00 AM – 12:00 PM)**")
        lines.append(f"- 🍳 **Breakfast:** {b_fast}")
        lines.append(f"- 🗺️ [Activity 1]: {act1}")
        lines.append(f"- 🗺️ [Activity 2]: {act2}")
        lines.append(f"- 🚌 **Transport:** {trans}")
        lines.append("")
        lines.append(f"**☀️ Afternoon (12:00 PM – 6:00 PM)**")
        lines.append(f"- 🍽️ **Lunch:** Local Restaurant (Signature Dish, ₹350)")
        lines.append(f"- 🗺️ [Activity 3]: Shopping at Local Emporium/Market")
        lines.append(f"- 🛍️ **Shopping/Leisure:** Buying souvenirs & local handicrafts")
        lines.append(f"- 🚌 **Transport:** Auto-rickshaw to evening hub (₹80)")
        lines.append("")
        lines.append(f"**🌙 Evening (6:00 PM – 10:00 PM)**")
        lines.append(f"- 🌆 [Evening activity]: Sunset views and street walk")
        lines.append(f"- 🍷 **Dinner:** Fine Dining Restaurant (Local cuisine, ₹1,200)")
        lines.append(f"- 🎵 **After Dinner:** Light & Sound Show or Night Market stroll")
        lines.append("")
        lines.append(f"**💡 Local Tips for Day {day_num}:**")
        lines.append(f"- Dress modestly when visiting cultural and religious sites.")
        lines.append(f"- Stay hydrated and drink bottled mineral water.")
        lines.append("")
        lines.append(f"**💰 Estimated Daily Budget:** ₹2,500 – ₹4,000 per person")
        lines.append("")
        lines.append("---")
        lines.append("")
        
    lines.append("### 🎒 Packing Tips")
    lines.append("- Comfortable walking shoes, sunscreen, sunglasses, and a hat.")
    lines.append("- Modest clothing covering shoulders and knees for temple visits.")
    lines.append("- Hand sanitizer and essential medications.")
    lines.append("")
    lines.append("### 📋 Essential Info")
    lines.append("- **Visa:** Check requirements before arrival.")
    lines.append("- **Currency:** Local currency. Credit cards accepted at major hubs, cash preferred at small stalls.")
    lines.append("- **Emergency Numbers:** 112 (All-in-one helpline).")
    lines.append("- **Best Apps:** Google Maps for navigation, Uber / local taxi apps for transport.")
    
    return "\n".join(lines)

