import re

# The scale is transformed to an arbitrary scale which is based on the austrialian scale
# but since it is not continuous I introduced decimals.

UIAA = {
    '1': 6,
    '2': 7,
    '3': 8,
    '3+': 9,
    '4-': 10,
    '4': 10.5,
    '4+': 11,
    '5-': 12,
    '5': 13,
    '5+': 14,
    '6-': 15,
    '6-/6': 16,
    '6': 17,
    '6/6+': 17.5,
    '6+': 18,
    '6+/7-': 18.5,
    '7-': 19,
    '7-/7': 19.5,
    '7': 20,
    '7/7+': 20.25,
    '7+': 20.5,
    '7+/8-': 21,
    '8-': 22,
    '8-/8': 23,
    '8': 24,
    '8/8+': 24.5,
    '8+': 25,
    '8+/9-': 26,
    '9-': 27,
    '9-/9': 27.5,
    '9': 28,
    '9/9+': 28.5,
    '9+': 29,
    '9+/10-': 29.5,
    '10-': 30,
    '10-/10': 30.5,
    '10': 31,
    '10/10+': 31.5,
    '10+': 32,
    '10+/11-': 32.5,
    '11-': 33,
    '11-/11': 34,
    '11': 35
}

French = {
    '3a': 7,
    '3b': 8,
    '3c': 9,
    '4a': 10,
    '4b': 11,
    '4b+': 12,
    '4c': 13,
    '4c+': 13.5,
    '5a': 14,
    '5a+': 14.5,
    '5b': 15,
    '5b+': 16,
    '5c': 17,
    '5c+': 17.5,
    '6a': 18,
    '6a+': 19,
    '6a+/6b': 19.5,
    '6b': 20,
    '6b+': 20.5,
    '6b+/6c': 21,
    '6c': 22,
    '6c/6c+': 22.5,
    '6c+': 23,
    '6c+/7a': 23.5,
    '7a': 24,
    '7a/7a+': 24.5,
    '7a+': 25,
    '7a+/7b': 25.5,
    '7b': 26,
    '7b/7b+': 26.5,
    '7b+': 27,
    '7b+/7c': 27.5,
    '7c': 28,
    '7c/7c+': 28.5,
    '7c+': 29,
    '7c+/8a': 29.25,
    '8a': 29.5,
    '8a/8a+': 29.75,
    '8a+': 30,
    '8a+/8b': 30.5,
    '8b': 31,
    '8b/8b+': 31.5,
    '8b+': 32,
    '8b+/8c': 32.5,
    '8c': 33,
    '8c/8c+': 33.5,
    '8c+': 34,
    '8c+/9a': 34.5,
    '9a': 35
}

# Slash grades are kind of messy...
YDS = {
    '5.3': 9,
    '5.4': 10,
    '5.5': 11,
    '5.6': 13,
    '5.7': 14,
    '5.7+': 14.5,
    '5.8': 15,
    '5.9': 17,
    '5.10a': 18,
    '5.10a/b': 18.5,
    '5.10b': 19,
    '5.10b/c': 19.5,
    '5.10c': 20,
    '5.10+': 20.25, # experimental, to be confirmed
    '5.10c/d': 20.25, # to be confirmed, skewed?
    '5.10d': 20.5,
    '5.11a': 21,
    '5.11a/b': 21.5,
    '5.11b': 22,
    '5.11b/c': 22.5,
    '5.11c': 23,
    '5.11c/d': 23.5,
    '5.11d': 24,
    '5.12a': 25,
    '5.12a/b': 25.5,
    '5.12b': 26,
    '5.12b/c': 26.5,
    '5.12c': 27,
    '5.12c/d': 27.5,
    '5.12d': 28,
    '5.12d/13a': 28.5,
    '5.13a': 29,
    '5.13a/b': 29.25,
    '5.13b': 29.5,
    '5.13b/c': 29.75,
    '5.13c': 30,
    '5.13c/d': 30.5,
    '5.13d': 31,
    '5.13d/14a': 31.5,
    '5.14a': 32,
    '5.14b': 33,
    '5.14c': 34,
    '5.14d': 35
}

Elbsandstein = {
    'II': 7, 
    'III': 8,
    'VI': 10,
    'V': 11,
    'VI': 13,
    'VIIa': 15,
    'VIIb': 17,
    'VIIc': 18,
    'VIIIa': 19,
    'VIIIb': 20,
    'VIIIc': 21,
    'IXa': 23,
    'IXb': 24,
    'IXc': 25,
    'Xa': 27,
    'Xb': 28,
    'Xc': 29,
    'XIa': 30,
    'XIb': 31,
    'XIc': 32,
    'XIIa': 33,
    'XIIa/XIIb': 34,
    'XIIb': 35
}

v_max = 17
v_keys = ["V" + str(x) for x in range(0, v_max)]
v_vals = range(0, v_max)
Vermin = dict(zip(v_keys, v_vals))
v_slashes_keys = [f"V{x}/{x+1}" for x in range(0, v_max)]
v_slashes_vals = [x + 0.5 for x in range(0, v_max)]
V_slashes = dict(zip(v_slashes_keys, v_slashes_vals))
Vermin.update(V_slashes)
Vermin.update({'VB': 0, 'L': 0})

Font = {
    '4': 0.,
    '5A': 1,
    '5B': 1.5,
    '5B+': 1.75,
    '5C': 2,
    '6A': 2.5,
    '6A/+': 2.75,
    '6A+': 3,
    '6B': 4,
    '6B/+': 4.25,
    '6B+': 4.5,
    '6C': 5,
    '6C/+': 5.25,
    '6C+': 5.5,
    '6C+/7A': 5.75,
    '7A': 6.25,
    '7A/+': 6.5,
    '7A+': 7,
    '7A+/B': 7.5,
    '7B': 8,
    '7B/+': 8.25,
    '7B+': 8.5,
    '7B+/C': 8.75,
    '7C': 9,
    '7C/+': 9.5,
    '7C+': 10,
    '7C+/8A': 10.5,
    '8A': 11,
    '8A/+': 11.5,
    '8A+': 12,
    '8A+/B': 12.5,
    '8B': 13,
    '8B/+': 13.5,
    '8B+': 14,
    '8B+/C': 14.5,
    '8C': 15,
    '8C/+': 15.5,
    '8C+': 16,
    '8C+/9A': 16.5,
    '9A': 17
}

Ole_to_UIAA = {v: k for k, v in UIAA.items()}
Ole_to_French = {v: k for k, v in French.items()}
Ole_to_YDS = {v: k for k, v in YDS.items()}
Ole_to_Elbsandstein = {v: k for k, v in Elbsandstein.items()}
Ole_to_Vermin = {v: k for k, v in Vermin.items()}
Ole_to_Font = {v: k for k, v in Font.items()}

class Grade:
    def __init__(self, value):
        self.value = str(value)

    def __repr__(self):
        return str(self.value)

    def get_scale(self):
        scale = "undetermined"

        yds_pattern = re.compile("5\.[1-9]+[a-d]?")
        french_pattern = re.compile("[1-9][a-z]+")
        uiaa_pattern = re.compile("[1-9]+[+-]?")
        elbsandstein_pattern = re.compile("[IVX]+[abc]?")
        vscale_pattern = re.compile("V[0-9]+")
        font_pattern = re.compile("[1-9][A-Z]+\+?")

        # Attention! Sequence currently matters (Elbsandstein V and V5
        # boulder have same regex right now)
        if yds_pattern.match(self.value):
            scale = "YDS"
        elif vscale_pattern.match(self.value) or self.value == "VB" or self.value == "L":
            scale = "Vermin"
        elif font_pattern.match(self.value):
            scale = "Font"
        elif elbsandstein_pattern.match(self.value):
            scale = "Elbsandstein"
        elif french_pattern.match(self.value):
            scale = "French"
        elif uiaa_pattern.match(self.value):
            scale = "UIAA"

        return scale

    def conv_grade(self):
        scale = self.get_scale()

        conversions = {
            'UIAA': UIAA,
            'French': French,
            'Elbsandstein': Elbsandstein,
            'YDS': YDS,
            'Vermin': Vermin,
            'Font': Font
        }

        # Handle the aid climbing scale: If the route is, e.g., 5.8 C2, treat it as 5.8 instead
        if ("R" in self.value or "C" in self.value or "A" in self.value):
            self.value = self.value.split(" ")[0]

        # Handle double Elbsandstein/French grade: Treat Xa/7c+ as Xa
        # (assuming that Elbsandstein has no slash grades!)
        if (scale == "Elbsandstein" and "/" in self.value):
            self.value = self.value.split("/")[0]
            
        # Handle traverse grades by subtracting 1 from ole_scale
        # IS THIS ONLY FRANKENJURA CONVENTION!?
        if ("trav" in self.value):
            return conversions[scale][self.value.split(" trav")[0]] - 1
            
        if scale == "undetermined" or self.value not in conversions[scale]:
            # print("The conversion factor", self.value, "is not in the dictonary, setting grade to 0")
            return 0

        return conversions[scale][self.value]

    @staticmethod
    def from_ole_grade(ole_value: float, target_system: str) -> str:
        """
        Convert from ole_grade (numeric) back to a grading system.

        :param ole_value: The numeric ole_grade value
        :param target_system: Target system ('French', 'UIAA', 'YDS', 'Elbsandstein', 'Vermin', 'Font')
        :returns: Grade string in target system
        """
        conversions = {
            'French': Ole_to_French,
            'UIAA': Ole_to_UIAA,
            'YDS': Ole_to_YDS,
            'Elbsandstein': Ole_to_Elbsandstein,
            'Vermin': Ole_to_Vermin,
            'Font': Ole_to_Font
        }

        # Direct lookup
        if ole_value in conversions[target_system]:
            return conversions[target_system][ole_value]

        # If exact match not found, find closest lower grade
        # This handles cases where ole_grade doesn't exactly match
        reverse_dict = conversions[target_system]
        available_grades = sorted(reverse_dict.keys())

        for i in range(len(available_grades)-1, -1, -1):
            if available_grades[i] <= ole_value:
                return reverse_dict[available_grades[i]]
