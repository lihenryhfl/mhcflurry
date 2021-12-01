"""
Reassign affinity values for mass spec data
"""
import sys
import os
import argparse

import pandas
import numpy as np

parser = argparse.ArgumentParser(usage=__doc__)

parser.add_argument("data", metavar="CSV", help="Training data")
parser.add_argument("--ms-only", action="store_true", default=False)
parser.add_argument("--drop-negative-ms", action="store_true", default=False)
parser.add_argument("--set-measurement-value", type=float)
parser.add_argument("--out-csv")
parser.add_argument("--test-out-csv")

pandas.set_option('display.max_columns', 500)


def go(args):
    df = pandas.read_csv(args.data)
    print(df)

    if args.drop_negative_ms:
        bad = df.loc[
            (df.measurement_kind == "mass_spec") &
            (df.measurement_inequality != "<")
        ]
        print("Dropping ", len(bad))
        df = df.loc[~df.index.isin(bad.index)].copy()

    if args.ms_only:
        print("Filtering to MS only")
        df = df.loc[df.measurement_kind == "mass_spec"].copy()

    if args.set_measurement_value is not None:
        indexer = df.measurement_kind == "mass_spec"
        df.loc[
            indexer,
            "measurement_value"
        ] = args.set_measurement_value
        print("Reassigned:")
        print(df.loc[indexer])

    if args.out_csv:
        if args.test_out_csv:
            df, df_test = split_train_test(df, debug=True)
            test_out_csv = os.path.abspath(args.test_out_csv)
            df_test.to_csv(test_out_csv, index=False)
            print("Wrote", test_out_csv)

        out_csv = os.path.abspath(args.out_csv)
        df.to_csv(out_csv, index=False)
        print("Wrote", out_csv)

def split_train_test(df, frac=0.8, debug=False):
    # for each allele, get idx of all occurrences in df
    allele2idx = {}
    for i, allele in enumerate(df.allele):
        if allele not in allele2idx:
            allele2idx[allele] = []
        allele2idx[allele].append(i)

    # split alleles according to frac
    np.random.seed(0)
    alleles = np.array([k for k in allele2idx])
    alleles = np.random.permutation(alleles)
    split_idx = int(len(alleles) * frac)

    train_alleles, test_alleles = alleles[:split_idx], alleles[split_idx:]

    # collect indices according to train and test split
    train_idx = []
    [train_idx.extend(allele2idx[allele]) for allele in train_alleles]

    test_idx = []
    [test_idx.extend(allele2idx[allele]) for allele in test_alleles]

    df_train, df_test = df.iloc[train_idx], df.iloc[test_idx]

    if debug:
        for allele in df_train.allele:
            assert allele in train_alleles

        for allele in df_test.allele:
            assert allele in test_alleles

    return df_train, df_test

if __name__ == "__main__":
    go(parser.parse_args(sys.argv[1:]))
