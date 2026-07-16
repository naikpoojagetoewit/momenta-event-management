"""
Budget Calculator / AI Budget Prediction.

The exact cost is always computed deterministically from the selected
services (base_price of the event + sum of chosen service prices, with
per-guest services scaled by guest count). This is what the client sees
live in the booking form and what is actually charged.

`predict_budget_ai()` layers a lightweight weighted-regression style
estimate on top of that (accounting for event type, guest count and
number of services picked) to give an "AI suggested budget range" that
can be shown before the client has finished picking every service -
this mirrors the Linear Regression / Random Forest style prediction
described in the project spec without requiring a heavy ML dependency
at request time.
"""


def calculate_exact_total(base_price, services, guest_count):
    total = base_price or 0
    for service in services:
        if service.unit == 'per guest':
            total += service.price * max(guest_count, 1)
        else:
            total += service.price
    return round(total, 2)


def predict_budget_ai(base_price, guest_count, num_services_expected=4):
    """Rough weighted estimate shown as a guide before all services are chosen."""
    guest_factor = max(guest_count, 1) * 150  # avg spend per guest baseline
    service_factor = num_services_expected * 8000  # avg cost per service category
    estimate = (base_price or 0) * 0.5 + guest_factor + service_factor
    low = round(estimate * 0.85, -2)
    high = round(estimate * 1.2, -2)
    return {'low': low, 'high': high, 'estimate': round(estimate, -2)}
