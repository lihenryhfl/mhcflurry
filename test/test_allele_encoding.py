import time

from mhcflurry.allele_encoding import AlleleEncoding
from mhcflurry.amino_acid import BLOSUM62_MATRIX
from nose.tools import eq_
from numpy.testing import assert_equal
import numpy
import pandas


def test_allele_encoding_speed():
    encoding = AlleleEncoding(
        ["A*02:01", "A*02:03", "A*02:01"],
        {
            "A*02:01": "AC",
            "A*02:03": "AE",
        }
    )
    start = time.time()
    encoding1 = encoding.fixed_length_vector_encoded_sequences("BLOSUM62")
    assert_equal(
        [
            [BLOSUM62_MATRIX["A"], BLOSUM62_MATRIX["C"]],
            [BLOSUM62_MATRIX["A"], BLOSUM62_MATRIX["E"]],
            [BLOSUM62_MATRIX["A"], BLOSUM62_MATRIX["C"]],
        ], encoding1)
    print("Simple encoding in %0.2f sec." % (time.time() - start))
    print(encoding1)

    encoding = AlleleEncoding(
        ["A*02:01", "A*02:03", "A*02:01"] * int(1e5),
        {
            "A*02:01": "AC" * 16,
            "A*02:03": "AE" * 16,
        }
    )
    start = time.time()
    encoding1 = encoding.fixed_length_vector_encoded_sequences("BLOSUM62")
    print("Long encoding in %0.2f sec." % (time.time() - start))


def test_allele_encoding_raw_values():
    encoding = AlleleEncoding(
        ["A*02:01", "A*02:03", "A*02:01"],
        pandas.DataFrame(
            [
                [0, 1, -1],
                [10, 11, 12],
            ],
            index=["A*02:01", "A*02:03"]))

    encoding1 = encoding.fixed_length_vector_encoded_sequences("BLOSUM62")
    assert_equal(
        [
            [0, 1, -1],
            [10, 11, 12],
            [0, 1, -1],
        ], numpy.array(encoding1))
