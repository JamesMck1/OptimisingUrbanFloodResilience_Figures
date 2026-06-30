# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 10:29:42 2024.

@author: James Mckenna

~~~ binary_encoding.py ~~~
Binary to integer conversion object enabling the conversion between a
bit-string and it's corresponding integer via a range of binary codings
(standard, unary and gray.)
"""

# Load Packages
import numpy as np
# import os
import logging

logger = logging.getLogger(__name__)

###############################################################################
# Base 36 encoding to reduce path length
###############################################################################

# --- BASE62 ALPHABET (0..35) ---
_BASE36_ALPHABET = (
    "0123456789abcdefghijklmnopqrstuvwxyz")
_BASE = len(_BASE36_ALPHABET)


def int_to_base36(n: int) -> str:
    """Encode a non-negative integer to base36 string."""
    if n < 0:
        raise ValueError("int_to_base36 only supports non-negative integers")
    if n == 0:
        return _BASE36_ALPHABET[0]
    digits = []
    while n:
        n, rem = divmod(n, _BASE)
        digits.append(_BASE36_ALPHABET[rem])
    return "".join(reversed(digits))


def base36_to_int(s: str) -> int:
    """Decode a base36 string back to integer."""
    val = 0
    for ch in s:
        idx = _BASE36_ALPHABET.find(ch)
        if idx == -1:
            raise ValueError(f"Invalid base36 character: {ch}")
        val = val * _BASE + idx
    return val


###############################################################################
# Helper functions for naming simulations with a unique integer
###############################################################################


def binary_to_sim_integer(binary_array):
    """Use a genotype to generate a unique integer to name simulation.

    Converts to a base36 representation to shorten the file path so that for
    large search spaces the path length doesn't exceed the limit.

    Parameters:
    binary_array (np.ndarray): A numpy array of '0's and '1's representing
    the binary genotype.

    Returns:
    sim_string : string
    The unique integer representation of the genotype converted to a base36
    string. Unique integer starts from 1 not 0.
    """
    # Convert the binary array to a string of binary digits
    binary_string = ''.join(binary_array.astype(int).astype(str))

    # Convert the binary string to an integer
    sim_integer = int(binary_string, 2) + 1  # start from 1 not 0

    # convert the integer to base36
    sim_string = int_to_base36(sim_integer)

    return sim_string


def sim_integer_to_binary(sim_string, length):
    """Convert a integer used to name a simulation to a binary coded array.

    Parameters:
    sim_string (str): The base36 encoded integer to convert.
    length (int): The desired length of the binary genotype.

    Returns:
    np.ndarray: A numpy array representing the binary genotype.
    """
    # convert from base36 to integer
    sim_integer = base36_to_int(sim_string)

    # Convert the integer to a binary string without the '0b' prefix
    # sim_integer - 1 to account for 1-indexing
    binary_string = bin(sim_integer-1)[2:]

    # Pad the binary string with leading zeros to match the desired length
    padded_binary_string = binary_string.zfill(length)

    # Convert the padded binary string to a numpy array of integers
    binary_array = np.array([int(bit) for bit in padded_binary_string])

    return binary_array


###############################################################################
# Standard binary coding
###############################################################################


class standard_binary_converter():
    """Convert bit-string <-> integer via standard binary coding."""

    def __init__(self):
        """Initialise object."""
        pass

    def binary_to_integer(self, binary_array):
        """Convert a binary genotype numpy array to a integer.

        Parameters:
        binary_array (np.ndarray): A numpy array of '0's and '1's representing
        the binary genotype.

        Returns:
        int: The unique integer representation of the genotype according to the
        selected binary coding method.
        """
        # Convert the binary array to a string of binary digits
        binary_string = ''.join(binary_array.astype(int).astype(str))

        # Convert the binary string to an integer
        integer_representation = int(binary_string, 2)

        return integer_representation

    def integer_to_binary(self, integer, length):
        """Convert an integer to a binary numpy array of a given length.

        Parameters:
        integer (int): The integer to convert.
        length (int): The desired length of the binary genotype.

        Returns:
        np.ndarray: A numpy array representing the binary genotype.
        """
        # Convert the integer to a binary string without the '0b' prefix
        binary_string = bin(integer)[2:]

        # Pad the binary string with leading zeros to match the desired length
        padded_binary_string = binary_string.zfill(length)

        # Convert the padded binary string to a numpy array of integers
        binary_array = np.array([int(bit) for bit in padded_binary_string])

        return binary_array


###############################################################################
# Gray coding
###############################################################################


def gray_to_binary(gray_array):
    """Convert from gray code to standard binary code."""
    # Initialize the binary code array with the same shape as the Gray code
    binary_array = np.zeros_like(gray_array)

    # The first binary bit is the same as the first Gray code bit
    binary_array[0] = gray_array[0]

    # Iterate through the array and compute the cumulative XOR
    for i in range(1, len(gray_array)):
        binary_array[i] = binary_array[i - 1] ^ gray_array[i]

    return binary_array


# def binary_to_gray(binary_array):
#     """Convert from standard binary code to gray code."""
#     # Perform XOR between the binary array and a shifted version of itself
#     gray_array = np.bitwise_xor(binary_array, np.roll(binary_array, -1))

#     # Ensure the last bit remains unchanged (Gray code for that bit)
#     gray_array[-1] = binary_array[-1]

#     return (gray_array)


class gray_binary_converter():
    """Convert bit-string <-> integer via gray binary coding."""

    def __init__(self):
        """Initialise object."""
        pass

    def binary_to_integer(self, binary_array):
        """Convert a binary genotype numpy array to a integer.

        Parameters:
        binary_array (np.ndarray): A numpy array of '0's and '1's representing
        the binary genotype.

        Returns:
        int: The unique integer representation of the genotype according to the
        selected binary coding method.
        """
        # convert from standard binary to gray binary
        standard_binary_array = gray_to_binary(binary_array)
        # Convert the binary array to a string of binary digits
        binary_string = ''.join(standard_binary_array.astype(int).astype(str))

        # Convert the binary string to an integer
        integer_representation = int(binary_string, 2)  # 1-index not 0

        return integer_representation

    def integer_to_binary(self, integer, length):
        """Convert an integer to a binary numpy array of a given length.

        Parameters:
        integer (int): The integer to convert.
        length (int): The desired length of the binary genotype.

        Returns:
        np.ndarray: A numpy array representing the binary genotype.
        """
        # convert to a gray string
        gray_string = bin(integer ^ (integer >> 1))[2:]
        gray_string = gray_string.zfill(length)
        gray_array = np.array([int(bit) for bit in gray_string],
                              dtype=np.uint8)

        return gray_array


###############################################################################
# Unary coding
###############################################################################


class unary_binary_converter():
    """Convert bit-string <-> integer via unary binary coding."""

    def __init__(self):
        """Initialise object."""
        pass

    def binary_to_integer(self, binary_array):
        """Convert a binary genotype numpy array to a integer.

        Parameters:
        binary_array (np.ndarray): A numpy array of '0's and '1's representing
        the binary genotype.

        Returns:
        int: The unique integer representation of the genotype according to the
        selected binary coding method.
        """
        # Convert the binary string to an integer via summation of the bits
        integer_representation = sum(binary_array) + 1  # 1-index not 0

        return (integer_representation)

    def integer_to_binary(self, integer, length):
        """Convert an integer to a binary numpy array of a given length.

        Parameters:
        integer (int): The integer to convert.
        length (int): The desired length of the binary genotype.

        Returns:
        np.ndarray: A numpy array representing the binary genotype.
        """
        logging.info(
            'WARNING: Unary to binary mapping is not surjective, therefore '
            ' a unique bit-string cannot be determined from an integer '
            'input.')


###############################################################################
# Binary coder object
###############################################################################


class binary_coder():
    """Object enabling the bit-string <-> integer conversion."""

    def __init__(self, binary_coding='standard'):
        """Initialise object.

        Parameters
        ----------
        binary_coding : string, optional
            Key word string describing the choice of binary coding.
            The default is 'standard'. Options are: 'standard', 'gray' or
            'unary'.
        """
        self.binary_coding = binary_coding  # selected method of binary coding
        # initialise a converter
        if self.binary_coding == 'standard':
            self.converter = standard_binary_converter()
        elif self.binary_coding == 'gray':
            self.converter = gray_binary_converter()
        elif self.binary_coding == 'unary':
            self.converter = unary_binary_converter()
        else:
            raise ValueError(f"Unknown binary coding method: {binary_coding}"
                             "Select from: 'standard', 'gray' or 'unary'.")

    def binary_to_integer(self, binary_array):
        """Convert a binary genotype numpy array to a integer.

        Parameters:
        binary_array (np.ndarray): A numpy array of '0's and '1's representing
        the binary genotype.

        Returns:
        int: The unique integer representation of the genotype according to the
        selected binary coding method.
        """
        return self.converter.binary_to_integer(binary_array)

    def integer_to_binary(self, integer, length):
        """Convert an integer to a binary numpy array of a given length.

        Parameters:
        integer (int): The integer to convert.
        length (int): The desired length of the binary genotype.

        Returns:
        np.ndarray: A numpy array representing the binary genotype.
        """
        return self.converter.integer_to_binary(integer, length)


###############################################################################
# Testing
###############################################################################


if __name__ == "__main__":

    # methods = ['standard', 'gray', 'unary']
    methods = ['gray']

    for method in methods:
        logging.info(f'\n--- {method} binary coding ---')
        test = binary_coder(binary_coding=method)

        # unique_ids = ['2S']

        # bit_strings = [sim_integer_to_binary(sim_string, 12)
        #                for sim_string in unique_ids]

        # bit_strings = [np.array([0, 0]),
        #                np.array([0, 1]),
        #                np.array([1, 0]),
        #                np.array([1, 1])]
        # bit_strings = [np.array([0, 0, 0]),
        #                np.array([0, 0, 1]),
        #                np.array([0, 1, 0]),
        #                np.array([1, 0, 0]),
        #                np.array([0, 1, 1]),
        #                np.array([1, 0, 1]),
        #                np.array([1, 1, 0]),
        #                np.array([1, 1, 1])]
        # bit_strings = [np.array([0, 0, 0, 0]),
        #                np.array([1, 0, 0, 0]),
        #                np.array([0, 1, 0, 0]),
        #                np.array([0, 0, 1, 0]),
        #                np.array([0, 0, 0, 1]),
        #                np.array([1, 1, 0, 0]),
        #                np.array([1, 0, 1, 0]),
        #                np.array([1, 0, 0, 1]),
        #                np.array([0, 1, 1, 0]),
        #                np.array([0, 1, 0, 1]),
        #                np.array([0, 0, 1, 1]),
        #                np.array([1, 1, 1, 0]),
        #                np.array([1, 0, 1, 1]),
        #                np.array([1, 1, 0, 1]),
        #                np.array([0, 1, 1, 1]),
        #                np.array([1, 1, 1, 1])]
        bit_strings = [np.array([0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0]),
                       np.array([1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0]),
                       np.array([1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0]),
                       np.array([1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
                       np.array([1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1])]
        length = len(bit_strings[0])
        integers = np.arange(0, 2**length)

        print('\nConvert integers to binary')
        for integer in integers:
            string = test.integer_to_binary(integer, length)
            print(f'{integer} = {string}')

        print('\nConvert binary to integers')
        for string in bit_strings:
            integer = test.binary_to_integer(string)
            sim_integer = binary_to_sim_integer(string)
            print(f'{string} = {integer} '
                  f'(sim_int = {sim_integer})')

        #     # Efficient decoding using list comprehension
        #     characteristic_lengths = [2, 2, 2, 2, 2, 2]
        #     cumsum = np.cumsum([0] + characteristic_lengths[:-1])
        #     ints = [test.binary_to_integer(
        #             string[start:start + length])
        #             for start, length in zip(cumsum, characteristic_lengths)]

        #     feature_id = (f'h{ints[0]}r{ints[1]}'
        #                   f't{ints[2]}b{ints[3]}'
        #                   f'x{ints[4]}y{ints[5]}')

        #     print(f'{unique_id}: {string} = {integer} = {sim_integer}'
        #           f' = {feature_id}')
