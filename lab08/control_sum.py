import unittest
from hypothesis import given, settings, Verbosity
from hypothesis.strategies import binary


def calculate_checksum(given_bytes):
    mask = (1 << 16) - 1
    result = 0
    cur_number = 0
    for idx in range(len(given_bytes)):
        if idx % 2 == 0:
            result = (result + cur_number) & mask
            cur_number = 0

        cur_number = (cur_number << 8) + int(given_bytes[idx])

    result = (result + cur_number) & mask
    return result


def add_checksum(given_bytes):
    checksum = calculate_checksum(given_bytes)
    return ((1 << 16) - 1 - checksum).to_bytes(2) + given_bytes


def check(given_bytes_with_checksum):
    return calculate_checksum(given_bytes_with_checksum) == ((1 << 16) - 1)


class CheckSumTests(unittest.TestCase):
    def test_simple_checksum(self):
        actual = calculate_checksum(b"\0\0\0\1")
        self.assertEqual(1, actual)

    @settings(verbosity=Verbosity.normal)
    @given(binary(max_size=1000))
    def test_good_data(self, binary_data):
        data_with_checksum = add_checksum(binary_data)
        self.assertTrue(check(data_with_checksum))
    
    @settings(verbosity=Verbosity.normal)
    @given(binary(min_size=4, max_size=1000))
    def test_bad_data(self, binary_data):
        data_with_checksum = add_checksum(binary_data)
        new_byte = (data_with_checksum[3] + 1) % 256
        new_data = data_with_checksum[:3] + new_byte.to_bytes(1) + data_with_checksum[4:]
        self.assertFalse(check(new_data))



if __name__ == "__main__":
    unittest.main()
