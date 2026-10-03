# Department assignment based on predicted complaint category

DEPARTMENT_MAP = {
    "Waste Management": "Sanitation Department",
    "Street Light": "Electrical Department",
    "Roads & Potholes": "Road Maintenance Department",
    "Water Supply": "Water Department",
    "Drainage & Sewerage": "Drainage & Sewerage Department",
    "Public Safety": "Public Safety Department"
}


# Estimated response time based on priority.
# These are prototype estimates for the project,
# not official municipal service guarantees.

RESPONSE_TIME_MAP = {
    "High": "4–8 hours",
    "Medium": "24–48 hours",
    "Low": "3–5 days"
}


def get_department(category):
    return DEPARTMENT_MAP.get(
        category,
        "General Municipal Department"
    )


def get_response_time(priority):
    return RESPONSE_TIME_MAP.get(
        priority,
        "3–5 days"
    )