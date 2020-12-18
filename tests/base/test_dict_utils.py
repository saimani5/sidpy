# -*- coding: utf-8 -*-
"""
Created on Mon Sep  28 15:07:16 2020

@author: Suhas Somnath
"""
from __future__ import division, print_function, unicode_literals, \
    absolute_import
import unittest
import sys
sys.path.append("../../sidpy/")
from sidpy.base.dict_utils import *

if sys.version_info.major == 3:
    unicode = str


class TestFlattenDict(unittest.TestCase):

    def test_already_flat(self):
        test_dict = {'0': 0, '1': 1}
        result_dict = flatten_dict(test_dict)
        self.assertEqual(result_dict, test_dict)


    def test_two_level(self):
        test_dict = {'0': {'0':0, '1':1}, '1': {'0':0, '1':1}}
        result_dict = flatten_dict(test_dict)
        expected_dict = {'0-0':0, '0-1':1, '1-0':0, '1-1':1}
        self.assertEqual(result_dict, expected_dict)




    def test_five_level(self):
        test_dict = {}
        def new_dict(dictionary):
            dictionary['0'] = {'0':0}
            return dictionary['0']
        for i in range(1,6):
            test_dict = new_dict(test_dict)

    def test_non_str_keys(self):
        pass

    def test_invalid_separator(self):
        pass

    def test_not_dict_at_all(self):
        pass

    def test_value_is_list(self):
        # Going by what @gduscher added
        pass


class TestMergeDicts(unittest.TestCase):

    def test_blah(self):
        pass


class TestNestDict(unittest.TestCase):

    def test_not_dict(self):
        pass

    def test_invalid_separator(self):
        pass

    def test_empty_separator(self):
        pass

    def test_incorrect_separator(self):
        pass

    def test_already_nested_dict(self):
        pass

    def test_partially_nested_dict(self):
        pass

    def test_typical_flat_dict(self):
        pass

    def test_keys_are_not_str(self):
        pass


class TestNestedDictFromFlattenedKey(unittest.TestCase):

    def test_nothing_to_flatten(self):
        pass

    def test_multiple_key_val(self):
        pass

    def test_five_level_key(self):
        pass

    def test_not_a_dict_at_all(self):
        pass

    def test_invalid_sep(self):
        pass

    def test_wrong_separator(self):
        pass

    def test_key_is_not_str(self):
        pass


class TestPrintNestedDict(unittest.TestCase):

    def test_not_dict(self):
        pass

    def test_invalid_level_type(self):
        pass

    def test_flat_dict(self):
        pass

    def test_typical_nested_dict(self):
        pass


if __name__ == '__main__':
    unittest.main()
