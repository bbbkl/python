# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: tr_constraint_test.py
#
# description
"""\n\n
    Test TrConstraint class
"""

import unittest
import message_file_reader
import os.path

class TrConstraintTest(unittest.TestCase) :
    """test TrConstraint class"""
    def setUp(self):
        self._target = self.get_test_constraint()
    
    def tearDown(self):
        pass
        
    def get_test_constraint(self):
        return self.get_test_constraints()[0]
    
    def get_test_constraints(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_tr_constraint.txt')
        items = message_file_reader.read_message_file(testfile)
        return items

    def test_process_id(self):
        self.assertEqual('05-00489320-0060', self._target.process_id())
        
    def test_process_bereich_from(self):
        self.assertEqual('PPA', self._target.process_bereich_from())
        
    def test_part_process_from(self):
        self.assertEqual('353082', self._target.part_process_from())    
        
    def test_ident_akt_from(self):
        self.assertEqual('460640', self._target.ident_akt_from())
     
    def test_part_process_to(self):
        self.assertEqual('353082', self._target.part_process_to())   
        
    def test_ident_akt_to(self):
        self.assertEqual('460642', self._target.ident_akt_to())
        
    def test_transition_time(self):
        expected = 1
        self.assertEqual(expected, self._target.transition_time())
        
    def test_transition_time_unit(self):
        expected = 3
        self.assertEqual(expected, self._target.transition_time_unit())
        
    def test_dynamic_buffer_time(self):
        expected = 0
        self.assertEqual(expected, self._target.dynamic_buffer_time())
        
    def test_dynamic_buffer_time_unit(self):
        expected = 0
        self.assertEqual(expected, self._target.dynamic_buffer_time_unit())
        
    def test_aob(self):
        self.assertEqual(3, self._target.aob())

    def test_part_lot(self):
        self.assertFalse(self._target.part_lot())
        
    def test_zeitwahl(self):
        self.assertEqual('TRANSPORT', self._target.zeitwahl())   
        
    def test_quantity_part_lot(self):
        self.assertEqual(1.0, self._target.quantity_part_lot())
    
    def test_quantity_part_lot_je(self):
        self.assertEqual(1.0, self._target.quantity_part_lot_je())
    
    def test_test_process_bereich_to(self):
        self.assertEqual('PPA', self._target.process_bereich_to())
    
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')           
