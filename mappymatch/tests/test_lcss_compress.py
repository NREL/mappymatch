from unittest import TestCase

from mappymatch.matchers.lcss.constructs import CuttingPoint
from mappymatch.matchers.lcss.utils import compress


class TestLCSSMatcherCompress(TestCase):
    def test_compress_one_group_sorted(self):
        """
        This will test that a sorted list with one compressed group will return
        correctly
        """
        starting_list = [
            CuttingPoint(1),
            CuttingPoint(2),
            CuttingPoint(3),
            CuttingPoint(4),
            CuttingPoint(5),
        ]

        expected_stop = 1
        expected_list = [CuttingPoint(3)]
        count = 0
        for cutting_point in compress(starting_list):
            self.assertTrue(count < expected_stop)
            self.assertEqual(expected_list[count], cutting_point)
            count += 1

    def test_compress_one_group_unsorted(self):
        """
        This will test that a unsorted list with one compressed group will return
        correctly
        """
        starting_list = [
            CuttingPoint(4),
            CuttingPoint(1),
            CuttingPoint(3),
            CuttingPoint(5),
            CuttingPoint(2),
        ]

        expected_stop = 1
        expected_list = [CuttingPoint(3)]
        count = 0
        for cutting_point in compress(starting_list):
            self.assertTrue(count < expected_stop)
            self.assertEqual(expected_list[count], cutting_point)
            count += 1

    def test_compress_multi_single_groups(self):
        """
        This will test that a sorted list multiple compressed groups of size 1 will
        result correctly
        """
        starting_list = [
            CuttingPoint(1),
            CuttingPoint(3),
            CuttingPoint(6),
            CuttingPoint(10),
            CuttingPoint(15),
        ]

        expected_stop = 5
        expected_list = [
            CuttingPoint(1),
            CuttingPoint(3),
            CuttingPoint(6),
            CuttingPoint(10),
            CuttingPoint(15),
        ]
        count = 0
        for cutting_point in compress(starting_list):
            self.assertTrue(count < expected_stop)
            self.assertEqual(expected_list[count], cutting_point)
            count += 1

    def test_compress_multi_groups(self):
        """
        This will test that a sorted list multiple compressed groups of various size
        will result correctly
        """
        starting_list = [
            CuttingPoint(1),
            CuttingPoint(2),
            CuttingPoint(6),
            CuttingPoint(7),
            CuttingPoint(8),
            CuttingPoint(11),
            CuttingPoint(12),
            CuttingPoint(13),
            CuttingPoint(14),
        ]

        expected_stop = 3
        expected_list = [
            CuttingPoint(2),
            CuttingPoint(7),
            CuttingPoint(13),
        ]
        count = 0
        for cutting_point in compress(starting_list):
            self.assertTrue(count < expected_stop)
            self.assertEqual(expected_list[count], cutting_point)
            count += 1
