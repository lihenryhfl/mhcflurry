import pandas
import numpy as np

from . import amino_acid


class AlleleEncoding(object):
    def __init__(self, alleles=None, allele_to_sequence=None, borrow_from=None):
        """
        A place to cache encodings for a sequence of alleles.

        We frequently work with alleles by integer indices, for example as
        inputs to neural networks. This class is used to map allele names to
        integer indices in a consistent way by keeping track of the universe
        of alleles under use, i.e. a distinction is made between the universe
        of supported alleles (what's in `allele_to_sequence`) and the actual
        set of alleles used for some task (what's in `alleles`).

        Parameters
        ----------
        alleles : list of string
            Allele names. If any allele is None instead of string, it will be
            mapped to the special index value -1.

        allele_to_sequence : dict of str -> str
            Allele name to amino acid sequence

        borrow_from : AlleleEncoding, optional
            If specified, do not specify allele_to_sequence. The sequences from
            the provided instance are used. This guarantees that the mappings
            from allele to index and from allele to sequence are the same
            between the instances.
        """

        if alleles is not None:
            alleles = pandas.Series(alleles)
        self.borrow_from = borrow_from
        self.allele_to_sequence = allele_to_sequence

        if self.borrow_from is None:
            assert allele_to_sequence is not None
            all_alleles = (
                sorted(allele_to_sequence))
            self.allele_to_index = dict(
                (allele, i)
                for (i, allele) in enumerate([None] + all_alleles))
            unpadded = pandas.Series([
                    allele_to_sequence[a] if a is not None else ""
                    for a in [None] + all_alleles
                ],
                index=[None] + all_alleles)
            self.sequences = unpadded.str.pad(
                unpadded.str.len().max(), fillchar="X")
        else:
            assert allele_to_sequence is None
            self.allele_to_index = borrow_from.allele_to_index
            self.sequences = borrow_from.sequences
            self.allele_to_sequence = borrow_from.allele_to_sequence

        if alleles is not None:
            assert all(
                allele in self.allele_to_index for allele in alleles),\
                "Missing alleles: " + " ".join(set(
                    a for a in alleles if a not in self.allele_to_index))
            self.indices = alleles.map(self.allele_to_index)
            assert not self.indices.isnull().any()
            self.alleles = alleles
        else:
            self.indices = None
            self.alleles = None

        self.encoding_cache = {}

    def compact(self):
        """
        Return a new AlleleEncoding in which the universe of supported alleles
        is only the alleles actually used.

        Returns
        -------
        AlleleEncoding
        """
        return AlleleEncoding(
            alleles=self.alleles,
            allele_to_sequence=dict(
                (allele, self.allele_to_sequence[allele])
                for allele in self.alleles.unique()
                if allele is not None))

    def allele_representations(self, encoding_name):
        """
        Encode the universe of supported allele sequences to a matrix.

        Parameters
        ----------
        encoding_name : string
            How to represent amino acids. Valid names are "BLOSUM62" or
            "one-hot". See `amino_acid.ENCODING_DATA_FRAMES`.

        Returns
        -------
        numpy.array of shape
            (num alleles in universe, sequence length, vector size)
        where vector size is usually 21 (20 amino acids + X character)
        """
        if self.borrow_from is not None:
            return self.borrow_from.allele_representations(encoding_name)

        cache_key = (
            "allele_representations",
            encoding_name)
        if cache_key not in self.encoding_cache:
            if encoding_name in ['BLOSUM62', 'one-hot']:
                index_encoded_matrix = amino_acid.index_encoding(
                    self.sequences.values,
                    amino_acid.AMINO_ACID_INDEX)
                vector_encoded = amino_acid.fixed_vectors_encoding(
                    index_encoded_matrix,
                    amino_acid.ENCODING_DATA_FRAMES[encoding_name])
            elif encoding_name in ['blosum62', 'esm_mean', 'protbert_mean', 'tape_mean']:
                mhcflurry_home = '/data/mhc/npz/'
                allele_names = np.load(mhcflurry_home + 'orig_allele_names_all.npy')
                mhc_str = np.load(mhcflurry_home + 'mhc_str_all.npy')
                mhc_pseudo_str = np.load(mhcflurry_home + 'mhc_pseudo_str_all.npy')
                vector_encoded = np.load(mhcflurry_home + 'mhc_feat_all_{}.npy'.format(encoding_name))

                # check that the loaded alleles are in the same order as the object's alleles
                # print(self.allele_to_index)
                allele_to_index_list = [(self.allele_to_index[allele], allele) for allele in self.allele_to_index]
                sorted_allele_to_index_list = sorted(allele_to_index_list, key=lambda x: x[0])
                # remove none
                assert sorted_allele_to_index_list[0][0] == 0 and sorted_allele_to_index_list[0][1] is None
                sorted_allele_to_index_list.pop(0)

                new_allele_to_index = dict([(allele, i) for (i, allele) in enumerate(allele_names)])
                new_allele_to_pseudo_str = dict([(allele, allele_str) for (allele_str, allele) in zip(mhc_pseudo_str, allele_names)])
                # print([x[1] for x in sorted_allele_to_index_list])

                def debug_name(name_str):
                    if 'Mafa-B*0' in name_str:
                        str1, str2 = name_str.split('*')
                        str2, str3 = str2.split(':')
                        if len(str2) == 3:
                            str2 = str2[1:]
                            name_str = str1 + '*' + str2 + ':' + str3

                    return name_str

                true_idx = [new_allele_to_index[debug_name(x[1])] for x in sorted_allele_to_index_list]
                try:
                    our_str = [new_allele_to_pseudo_str[debug_name(x[1])] for x in sorted_allele_to_index_list]
                    orig_str = [self.allele_to_sequence[x[1]] for x in sorted_allele_to_index_list]
                    for s1, s2 in zip(our_str, orig_str):
                        if s1 != s2:
                            print(s1)
                            print(s2)
                            print('\n')
                    # print([ours == orig for ours, orig in zip(our_str, orig_str)])
                    # assert all([ours == orig for ours, orig in zip(our_str, orig_str)]), + '\n' + str([len(x) for x in orig_str])
                except KeyError as ke:
                    print('Key Error!', ke)

                true_idx = np.array(true_idx).astype(int)
                # print('true_idx', true_idx)
                vector_encoded = vector_encoded[true_idx]
                # add the unknown vector back in (all zeros)
                tmp = np.zeros_like(vector_encoded[0:1])
                vector_encoded = np.concatenate([tmp, vector_encoded], axis=0)

                print("LOADED OUR NEW CUSTOM ALLELE_ENCODING!")
            self.encoding_cache[cache_key] = vector_encoded
        return self.encoding_cache[cache_key]

    def fixed_length_vector_encoded_sequences(self, encoding_name):
        """
        Encode allele sequences (not the universe of alleles) to a matrix.

        Parameters
        ----------
        encoding_name : string
            How to represent amino acids. Valid names are "BLOSUM62" or
            "one-hot". See `amino_acid.ENCODING_DATA_FRAMES`.

        Returns
        -------
        numpy.array with shape:
            (num alleles, sequence length, vector size)
        where vector size is usually 21 (20 amino acids + X character)
        """
        cache_key = (
            "fixed_length_vector_encoding",
            encoding_name)
        if cache_key not in self.encoding_cache:
            vector_encoded = self.allele_representations(encoding_name)
            result = vector_encoded[self.indices]
            self.encoding_cache[cache_key] = result
        return self.encoding_cache[cache_key]
