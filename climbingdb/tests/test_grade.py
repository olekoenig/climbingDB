"""
Run as
python3 -m unittest tests/test_grade.py
"""

import unittest

from ..grade import Grade

class TestGrades(unittest.TestCase):
    def test_sportclimbs(self):
        self.assertEqual(Grade("7c").get_scale(), "French")
        self.assertEqual(Grade("VIIIa").get_scale(), "Elbsandstein")
        self.assertEqual(Grade("V").get_scale(), "Elbsandstein")
        self.assertEqual(Grade("5.13b").conv_grade(), Grade("9+/10-").conv_grade())
        self.assertEqual(Grade("8a+").conv_grade(), Grade("10-").conv_grade())

    def test_boulders(self):
        self.assertEqual(Grade("V0").get_scale(), "Vermin")
        self.assertEqual(Grade("7B trav").get_scale(), "Font")
        self.assertEqual(Grade("7B trav").conv_grade(), Grade("7A+").conv_grade())
        self.assertEqual(Grade("7C+").get_scale(), "Font")
        self.assertEqual(Grade("V10").conv_grade(), Grade("7C+").conv_grade())

    # test5 = Grade("V")
    # print("Input: V")
    # print("The infered grading scale is {}".format(test5.get_scale()))
    # print("{} is translated to {} in Ole's internal scale".format(test5, test5.conv_grade()))

    # test6 = Grade("V9")
    # print("Input: V5")
    # print("The infered grading scale is {}".format(test6.get_scale()))
    # print("{} is translated to {} in Ole's internal scale".format(test6, test6.conv_grade()))

    # test7 = Grade("7C")
    # print("Input: 7C")
    # print("The infered grading scale is {}".format(test7.get_scale()))
    # print("{} is translated to {} in Ole's internal scale".format(test7, test7.conv_grade()))
    
if __name__ == "__main__":
    unittest.main()
    
