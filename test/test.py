import os
import sys
sys.path.insert(0, os.path.join(".."))

import unittest

import test_document_access

def suite():
    """
    Generates test suite
    """
    test_suite = unittest.TestSuite()
    test_suite.addTests(test_document_access.suite())
    return test_suite

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=1).run(suite())