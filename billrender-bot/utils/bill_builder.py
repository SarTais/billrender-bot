from billrender import (
    Bill,
    Apartment,
    MeteredUtility,
    FixedUtility,
    PrecalculatedUtility,
)
from datetime import date


def build_bill(settings, data: dict) -> Bill:
    apartment = Apartment(name=settings.apartment_name)

    # Electricity
    el_data = data["electricity"]
    electricity = MeteredUtility(
        name="Electricity",  # el_data["name"],
        unit_label=el_data["unit_label"],
        unit_price=float(el_data["unit_price"]),
        previous_value=int(el_data["prev"]),
        current_value=int(el_data["current"]),
        fixed_price=float(el_data["fixed_price"]),
        icon="💡"
    )

    # Water
    water_data = data["water"]
    water = MeteredUtility(
        name="Cold Water",  # water_data["name"],
        unit_label=water_data["unit_label"],
        unit_price=float(water_data["unit_price"]),
        previous_value=int(water_data["prev"]),
        current_value=int(water_data["current"]),
        fixed_price=float(water_data["fixed_price"]),
        icon="🚰"
    )

    # Gas
    gas_data = data["gas"]
    gas = MeteredUtility(
        name="Gas", #gas_data["name"],
        unit_label=gas_data["unit_label"],
        unit_price=float(gas_data["unit_price"]),
        previous_value=int(gas_data["prev"]),
        current_value=int(gas_data["current"]),
        fixed_price=float(gas_data["fixed_price"]),
        icon="🔥"
    )

    heating_data = data["heating"]

    heating_amount = float(heating_data["amount"])
    heating_fixed_price = float(heating_data["fixed_price"])

    # If heating is effectively off (no usage), don't charge fixed price
    if heating_amount == 0:
        heating_fixed_price = 0.0

    heating = PrecalculatedUtility(
        name="Heating", #heating_data["name"],
        unit_label=heating_data["unit_label"],
        unit_price=float(heating_data["unit_price"]),
        amount=heating_amount,
        fixed_price=heating_fixed_price,
        icon="🌡"
    )

    # Trash utilisation: fixed-only
    trash_data = data["trash"]
    trash = FixedUtility(
        name="Trash Utilisation", #trash_data["name"],
        fixed_price=float(trash_data["amount"]),
        icon="🗑"
    )

    # House maintenance: fixed-only
    maintenance = FixedUtility(
        name="House Maintenance",
        fixed_price=float(data["maintenance_price"]),
        icon="🏠"
    )

    # Period and rent
    raw_start = data.get("period_start")
    raw_end = data.get("period_end")

    def _coerce_date(value):
        if isinstance(value, date):
            return value
        if isinstance(value, str) and value.strip():
            from datetime import datetime
            try:
                # try ISO format first
                return datetime.strptime(value.strip(), "%Y-%m-%d").date()
            except ValueError:
                # fallback to sheet format
                try:
                    return datetime.strptime(value.strip(), "%d.%m.%Y").date()
                except ValueError:
                    return date.today()
        return date.today()

    period_start = _coerce_date(raw_start)
    period_end = _coerce_date(raw_end)

    rent = float(data.get("rent", 0.0))

    return Bill(
        apartment=apartment,
        period_start=period_start,
        period_end=period_end,
        rent=rent,
        utilities=[gas, water, electricity, heating, trash, maintenance],
    )