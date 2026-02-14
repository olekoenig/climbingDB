"""
Helper functions for form rendering.
"""

from climbingdb.grade import French, UIAA, YDS, Elbsandstein, Vermin, Font


def get_grade_system_options(discipline):
    """Get available grading systems for discipline."""
    if discipline == "Boulder":
        return ["Vermin", "Font"]
    return ["French", "UIAA", "YDS", "Elbsandstein"]


def get_style_options(discipline):
    """Get available style options for discipline."""
    if discipline == "Boulder":
        return ["F"]
    elif discipline == "Sportclimb":
        return ["o.s.", "F", "2. Go", "toprope"]
    else:  # Multipitch
        return ["o.s.", "F", "AF", "followed"]


def get_grade_options(grade_system):
    """Get sorted grade options for a grading system."""
    grade_dict = eval(grade_system)  # French, UIAA, etc.
    return [""] + [k for k, v in sorted(grade_dict.items(), key=lambda x: x[1])]


def get_shortnote_options(discipline):
    """Get short note options for discipline."""
    shortnote = ["", "soft", "hard"]
    if discipline == "Boulder":
        shortnote.append("trav")
    else:
        shortnote.append("trad")
    return shortnote


def validate_route_data(name, grade, area, crag, country):
    """Validate required route fields."""
    errors = []
    if not name:
        errors.append("Route name is required!")
    if not grade:
        errors.append("Grade is required!")
    if not area or not crag or not country:
        errors.append("Country, area, and crag are required!")
    return errors
