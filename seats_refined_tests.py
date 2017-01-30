import unittest
import seats_refinedV1


class SeatsTest(unittest.TestCase):
    def test_count_list(self):
        self.assertEqual(seats_refinedV1.count_list(), )

    def test_count_str_list(self):
        self.assertEqual(seats_refinedV1.count_str_list(), )

    def test_read_database(self):
        self.assertEqual(seats_refinedV1.read_database(), )

    def test_read_csv(self):
        self.assertEqual(seats_refinedV1.read_csv(), )

    def test_assign_metrics_list(self):
        self.assertEqual(seats_refinedV1.test_assign_metrics(), )