"""Game locations S.T.A.L.K.E.R."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Location:
    name: str
    description: str
    connected_locations: list[str]
    required_level: int = 1
    shelter_unlocked: bool = False


LOCATIONS = {
    "city": Location(
        name="🏙️ City",
        description="Abandoned city-ghost. Building ruins, rusty cars...",
        connected_locations=["hospital", "market", "shelter"],
    ),
    "hospital": Location(
        name="🏥 Hospital",
        description="Half-destroyed hospital. You can find medicine here.",
        connected_locations=["city"],
    ),
    "market": Location(
        name="🛒 Black Market",
        description="Underground market of stalkers. Buy and sell items.",
        connected_locations=["city"],
    ),
    "shelter": Location(
        name="🔒 Shelter",
        description="Secret stalker shelter. Currently locked for you.",
        connected_locations=["city"],
        shelter_unlocked=True,
    ),
}


def get_location(location_id: str) -> Optional[Location]:
    return LOCATIONS.get(location_id)


def get_location_description(location_id: str, shelter_unlocked: bool = False) -> str:
    loc = get_location(location_id)
    if not loc:
        return "Unknown location"

    if location_id == "shelter" and not shelter_unlocked:
        return "🔒 Shelter\n\nYou stand in front of a massive metal door. It's locked.\nYou need to find a way to get inside..."

    return f"{loc.name}\n\n{loc.description}"


def get_available_moves(current_location: str, shelter_unlocked: bool = False) -> list[str]:
    loc = get_location(current_location)
    if not loc:
        return []

    available = []
    for loc_id in loc.connected_locations:
        if loc_id == "shelter" and not shelter_unlocked:
            continue
        available.append(loc_id)

    return available


def format_locations_list(locations: list[str]) -> str:
    if not locations:
        return "Nowhere to go"
    result = []
    for loc_id in locations:
        loc = get_location(loc_id)
        if loc:
            result.append(f"• {loc.name}")
    return "\n".join(result)
