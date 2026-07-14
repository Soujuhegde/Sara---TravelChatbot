from datetime import datetime, timedelta
from app.orchestrator.nlu_parser import resolve_relative_checkout
from app.orchestrator.hotel_flow import handle_hotel_clarification

def test_resolve_relative_checkout():
    check_in = "2026-08-15"
    
    # Test tomorrow
    assert resolve_relative_checkout(check_in, "Tomorrow") == "2026-08-16"
    assert resolve_relative_checkout(check_in, "tomorrow") == "2026-08-16"
    
    # Test day numbers
    assert resolve_relative_checkout(check_in, "In 2 days") == "2026-08-17"
    assert resolve_relative_checkout(check_in, "3 nights") == "2026-08-18"
    assert resolve_relative_checkout(check_in, "5 days") == "2026-08-20"
    
    # Test week
    assert resolve_relative_checkout(check_in, "1 week") == "2026-08-22"
    
    # Test empty or none inputs
    assert resolve_relative_checkout("", "Tomorrow") is None
    assert resolve_relative_checkout(check_in, "") is None

def test_price_cleaning_with_cents():
    # Test that price parsing correctly cleans prices with cents without multiplying by 100
    state = {
        "flight_params": {},
        "hotel_params": {
            "city": "Goa",
            "check_in_date": "2026-08-15",
            "check_out_date": "2026-08-17",  # 2 nights
            "guests": "1 Adult",
            "rooms": "1 Room"
        },
        "selected_hotel": {
            "name": "Luxury Resort",
            "price": "₹2,916.00"  # has cents
        }
    }
    
    res = handle_hotel_clarification("hotel_summary", state)
    msg = res["final_response"]
    
    # Expected total price: 2916 * 2 nights * 1 room = 5832
    assert "Total Price: ₹5,832.00" in msg
    assert "Check-in: 2026-08-15" in msg
    assert "Check-out: 2026-08-17" in msg

from langchain_core.messages import AIMessage, HumanMessage
from app.orchestrator.nlu_parser import parse_intent

def test_passport_extraction_no_interruption():
    # Test that providing a passport number (e.g. "AR436878") at awaiting_passenger_details
    # is parsed with the AIMessage context and NOT flagged as an interruption question.
    state = {
        "current_step": "awaiting_passenger_details",
        "passenger_count": {"adults": 1, "children": 0, "infants": 0, "total": 1},
        "passengers_details": [{"name": "John Doe", "email": "john@gmail.com", "contact": "+919876543210"}],
        "current_passenger_index": 0,
        "messages": [
            AIMessage(content="Please provide the Passport No for Passenger 1 of 1 to proceed."),
            HumanMessage(content="AR436878")
        ]
    }
    
    # Run parse_intent
    new_state = parse_intent(state)
    
    # 1. Verify that it was NOT flagged as an interruption
    assert new_state.get("interruption_question") is None
    
    # 2. Verify that it extracted the passport number correctly
    pax = new_state["passengers_details"][0]
    assert pax.get("passport") == "AR436878"
    assert new_state["current_step"] == "awaiting_payment"
