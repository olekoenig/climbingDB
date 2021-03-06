import re

# The scale is transformed to an arbitrary scale which is based on the austrialian scale
# but since it is not continuous I introduced decimals.

# To Do: Need to introduce Saxonian scale!

UIAA = {
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


class Grade:
    def __init__(self, value):
        self.value = str(value)

    def __repr__(self):
        return str(self.value)
        
    def get_scale(self):
        status = "undetermined"
        french_pattern = re.compile('[1-9][a-z]+')

        #print(self.value, type(self.value))
        
        if "5." in self.value:
            status = "YDS"
        elif french_pattern.match(self.value):
            status = "French"
        elif status == "undetermined":
            status = "UIAA"
        else:
            print("Could not identify the difficulty scale.")
        return status

    
    def conv_grade(self):
        region = self.get_scale()
        conversions = {
            'UIAA': UIAA,
            'French': French,
            'YDS': YDS
        }

        # Handle the aid climbing scale: If the route is, e.g., 5.8 C2, treat it as 5.8 instead
        if ("R" in self.value or "C" in self.value or "A" in self.value):
            self.value = self.value.split(" ")[0]

        # Test if the grade is in Ole's grade conversion table
        if self.value not in conversions[region]:
            # print("The conversion factor", self.value, "is not in the dictonary, setting grade to 0")
            return 0

        return conversions[region][self.value]


if __name__ == "__main__":
    test = Grade("5.13a")
    print("Input: 5.13a")
    print("The infered grading scale is {}".format(test.get_scale()))
    print("{} is translated to {} in Ole's internal scale".format(test,test.conv_grade()))
