import re

# The scale is transformed to an arbitrary scale which is based on the austrialian scale
# but since it is not continuous I introduced decimals.

# To Do: Need to introduce Saxonian scale!

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
    '5a': 14,
    '5b': 15,
    '5b+': 16,
    '5c': 17,
    '5c+': 17.5,
    '6a': 18,
    '6a+': 19,
    '6a+/6b': 19.5,
    '6b': 20,
    '6b+': 20.5,
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

Ole_scale = {v: k for k, v in French.items()}


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

        if yds_pattern.match(self.value):  #"5." in self.value:
            scale = "YDS"
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
            'YDS': YDS
        }

        # Handle the aid climbing scale: If the route is, e.g., 5.8 C2, treat it as 5.8 instead
        if ("R" in self.value or "C" in self.value or "A" in self.value):
            self.value = self.value.split(" ")[0]

        # Handle double Elbsandstein/French grade: Treat Xa/7c+ as Xa
        # (assuming that Elbsandstein has no slash grades!)
        if (scale == "Elbsandstein" and "/" in self.value):
            self.value = self.value.split("/")[0]
            
        if scale == "undetermined" or self.value not in conversions[scale]:
            # print("The conversion factor", self.value, "is not in the dictonary, setting grade to 0")
            return 0

        return conversions[scale][self.value]


if __name__ == "__main__":
    test1 = Grade("5.13a")
    print("Input: 5.13a")
    print("The infered grading scale is {}".format(test1.get_scale()))
    print("{} is translated to {} in Ole's internal scale".format(test1, test1.conv_grade()))

    test2 = Grade("9+/10-")
    print("Input: 9+/10-")
    print("The infered grading scale is {}".format(test2.get_scale()))
    print("{} is translated to {} in Ole's internal scale".format(test2, test2.conv_grade()))

    test3 = Grade("VIIIa")
    print("Input: VIIIa")
    print("The infered grading scale is {}".format(test3.get_scale()))
    print("{} is translated to {} in Ole's internal scale".format(test3, test3.conv_grade()))

    test4 = Grade("8a")
    print("Input: 8a")
    print("The infered grading scale is {}".format(test4.get_scale()))
    print("{} is translated to {} in Ole's internal scale".format(test4, test4.conv_grade()))

    test5 = Grade("V")
    print("Input: V")
    print("The infered grading scale is {}".format(test5.get_scale()))
    print("{} is translated to {} in Ole's internal scale".format(test5, test5.conv_grade()))
