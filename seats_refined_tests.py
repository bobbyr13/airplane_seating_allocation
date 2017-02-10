import unittest
import seats_refinedV1


class SeatsTest(unittest.TestCase):

    sample_plane_list = ['', '', '', '']
    sample_plane_list2 = ['Donald Trump', 'Donald Trump', '', '']
    sample_plane_list3 = ['Donald Trump', 'Hilary Clinton', 'Hilary Clinton', 'Hilary Clinton',
                          '', 'Hilary Clinton', '', '']
    sample_row_length = 4
    sample_string = 'Donald Trump'
    sample_string2 = 'Hilary Clinton'
    sample_integer = 0
    sample_integer2 = 1

    def test_count_list(self):
        # row length 1 sample
        self.assertEqual(seats_refinedV1.count_list(self.sample_plane_list, self.sample_row_length,
                                                    self.sample_integer), 4)
        self.assertEqual(seats_refinedV1.count_list(self.sample_plane_list2, self.sample_row_length,
                                                    self.sample_integer), 2)
        self.assertEqual(seats_refinedV1.count_list(self.sample_plane_list3, self.sample_row_length,
                                                    self.sample_integer), 2)
        self.assertEqual(seats_refinedV1.count_list(self.sample_plane_list3, self.sample_row_length,
                                                    self.sample_integer2), 1)

    def test_count_str_list(self):
        self.assertEqual(seats_refinedV1.count_str_list(self.sample_plane_list, self.sample_string), 0)
        self.assertEqual(seats_refinedV1.count_str_list(self.sample_plane_list2, self.sample_string), 2)
        self.assertEqual(seats_refinedV1.count_str_list(self.sample_plane_list3, self.sample_string2), 4)

    def test_read_database(self):
        self.assertEqual(seats_refinedV1.read_database(db_file="database_for_testing.db"), (10, 'XYZ', 30))

    def test_read_csv(self):
        self.assertEqual(seats_refinedV1.read_csv(csv_file="test_booking.csv"),
                         (3, ['Bobby', 'Chris', 'Eoin'], ['2', '4', '3']))
