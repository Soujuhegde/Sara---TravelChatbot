from app.schemas.chat import TaskRequest, TaskResponse
import os
import time
import httpx
from datetime import datetime

def format_time(time_str: str) -> str:
    try:
        return time_str.split(" ")[1][:5]
    except:
        return time_str

def format_date(time_str: str) -> str:
    try:
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        return dt.strftime("%a, %d %b %y")
    except:
        return time_str

def call_flight_agent(request: TaskRequest) -> TaskResponse:
    params = request.parameters
    if not params.get("origin") or not params.get("destination") or not params.get("departure_date"):
        return TaskResponse(
            task_id=request.task_id,
            status="needs_clarification",
            clarification_needed="I need the origin, destination, and departure date to search for flights.",
            metadata={"agent_id": "flight_agent", "timestamp": time.time()}
        )
    
    api_key = os.getenv("SERPAPI_API_KEY")
    results = []

    if api_key:
        try:
            url = "https://serpapi.com/search.json"
            req_params = {
                "engine": "google_flights",
                "departure_id": params.get("origin"),
                "arrival_id": params.get("destination"),
                "outbound_date": params.get("departure_date"),
                "currency": "INR",
                "hl": "en",
                "type": "2",
                "api_key": api_key
            }
            
            response = httpx.get(url, params=req_params, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            
            google_flights_url = data.get("search_metadata", {}).get("google_flights_url", "https://flights.google.com")
            
            best_flights = data.get("best_flights", [])
            other_flights = data.get("other_flights", [])
            flights = best_flights + other_flights
                
            seen_flight_numbers = set()
            
            def add_flight(f):
                first_leg = f.get("flights", [{}])[0]
                last_leg = f.get("flights", [{}])[-1]
                flight_number = first_leg.get("flight_number", "Unknown")
                
                if flight_number in seen_flight_numbers and flight_number != "Unknown":
                    return False
                seen_flight_numbers.add(flight_number)
                
                airline = first_leg.get("airline", "Unknown Airline")
                logo = first_leg.get("airline_logo", "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Air_India_Logo.svg/512px-Air_India_Logo.svg.png")
                
                dep = first_leg.get("departure_airport", {})
                arr = last_leg.get("arrival_airport", {})
                dep_time_raw = dep.get("time", "")
                arr_time_raw = arr.get("time", "")
                
                duration = str(f.get("total_duration", "Unknown")) + "m" if isinstance(f.get("total_duration"), int) else f.get("duration", "Unknown")
                
                stops_count = len(f.get("flights", [])) - 1
                stops_str = "Non-stop" if stops_count == 0 else f"Connecting Flight ({stops_count} Stop{'s' if stops_count > 1 else ''})"
                base_price = f.get("price", 0)
                
                origin_code = dep.get('id', params.get('origin', ''))
                destination_code = arr.get('id', params.get('destination', ''))
                
                custom_link = google_flights_url
                try:
                    num = flight_number.split(" ")[-1] if " " in flight_number else flight_number
                    airline_lower = airline.lower()
                    if airline_lower == "indigo":
                        custom_link = f"https://www.goindigo.in/book/flight-select.html?cid=metasearch|googleflights&fareType=R&flightNumber={num}&origin={origin_code}&destination={destination_code}"
                    elif airline_lower == "air india express":
                        custom_link = f"https://www.airindiaexpress.com/book?flightNumber={num}&origin={origin_code}&destination={destination_code}"
                    elif airline_lower == "air india":
                        custom_link = f"https://www.airindia.com/in/en/ibe/booking.html?flightNumber={num}&origin={origin_code}&destination={destination_code}#/availability/departure"
                    elif "srilankan" in airline_lower:
                        custom_link = f"https://www.srilankan.com/en_uk/plan-and-book/flight-selection?origin={origin_code}&destination={destination_code}&flightNumber={num}"
                except:
                    pass
                
                if base_price:
                    formatted_base = f"INR {base_price:,.2f}"
                    formatted_prem = f"INR {int(base_price * 1.35):,.2f}"
                    formatted_bus = f"INR {int(base_price * 2.8):,.2f}"
                else:
                    formatted_base = "Price unavailable"
                    formatted_prem = "Price unavailable"
                    formatted_bus = "Price unavailable"

                card = {
                    "airline_name": airline,
                    "airline_logo": logo,
                    "flight_numbers": flight_number,
                    "departure_date": format_date(dep_time_raw) if dep_time_raw else params.get("departure_date"),
                    "arrival_date": format_date(arr_time_raw) if arr_time_raw else params.get("departure_date"),
                    "departure_time": format_time(dep_time_raw) if dep_time_raw else "00:00",
                    "arrival_time": format_time(arr_time_raw) if arr_time_raw else "00:00",
                    "origin_airport": f"{dep.get('name', 'Origin')} ({dep.get('id', params.get('origin'))})",
                    "destination_airport": f"{arr.get('name', 'Destination')} ({arr.get('id', params.get('destination'))})",
                    "duration": duration,
                    "stops": stops_str,
                    "booking_link": custom_link,
                    "pricing": [
                        {"class": "Economy", "price": formatted_base},
                        {"class": "Premium Economy", "price": formatted_prem},
                        {"class": "Business", "price": formatted_bus}
                    ]
                }
                results.append(card)
                return True

            limit = params.get("limit", 5)
            seen_airlines = set()
            for f in flights:
                if len(results) >= limit:
                    break
                flight_info = f.get("flights", [{}])[0]
                airline = flight_info.get("airline", "Unknown Airline")
                if airline not in seen_airlines:
                    if add_flight(f):
                        seen_airlines.add(airline)
            
            if len(results) < limit:
                for f in flights:
                    if len(results) >= limit:
                        break
                    add_flight(f)
        except Exception as e:
            print(f"SerpAPI Error: {e}")

    # If no results were found (past date, API error, etc.), do not fallback to mock data as per user request.
    if not results:
        print("No real-time flights found.")

    return TaskResponse(
        task_id=request.task_id,
        status="success",
        results=results,
        metadata={"agent_id": "flight_agent", "timestamp": time.time(), "source": "serpapi" if api_key and results else "mock"}
    )
