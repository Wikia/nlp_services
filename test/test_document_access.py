import sys

from nlp_services.document_access import document_access
import os

sys.path.insert(0, os.path.join(".."))

from mock import patch, Mock, MagicMock
import unittest


class MockBucket(Mock):
    pass


class MockS3Connection(Mock):

    def get_bucket(self, bucket_name):
        if not hasattr(self, 'called'):
            self.called = 0
        assert bucket_name == 'nlp-data'
        self.called += 1
        return MockBucket()


class MockDocument(Mock):
    pass


class TestFunctions(unittest.TestCase):

    def test_get_s3_bucket(self):
        self.assertIsNone(document_access.S3_BUCKET, "S3 bucket should be lazy-loaded")
        conn = MockS3Connection()
        with patch('nlp_services.document_access.connect_s3', Mock(return_value=conn)):
            self.assertIsInstance(document_access.get_s3_bucket(), MockBucket)
            self.assertIsInstance(document_access.S3_BUCKET, MockBucket, "S3 bucket should be memoized")
            self.assertIsInstance(document_access.get_s3_bucket(), MockBucket)
            self.assertEquals(1, conn.called)

    def test_get_document_by_id_returns_none(self):
        service = MagicMock()
        service.get = Mock(return_value=500)
        with patch('nlp_services.document_access.ParsedXmlService'):
            self.assertIsNone(document_access.get_document_by_id('123_321'))

    def test_get_document_by_id_returns_document(self):
        get_mock = Mock(name='get', return_value={'status': 200, '123_321': '<xml/>'})
        with patch('nlp_services.document_access.Document', MockDocument):
            with patch('nlp_services.document_access.ParsedXmlService.get', get_mock):
                doc = document_access.get_document_by_id('123_321')
                self.assertIsInstance(doc, MockDocument)


def suite():
    """
    Generates test suite
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestFunctions))
    return test_suite

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=1).run(suite())