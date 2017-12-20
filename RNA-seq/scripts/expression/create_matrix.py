#!/usr/bin/env python3
# @Author: Anthony Federico

import pandas as pd
import sys

def aggregate_counts(files, method):
    """
    Merges count files into a single pandas dataframe

    Args:
        Param #1 (list): List of paths to count files
    Returns:
        Pandas dataframe
    """      
    counts = {}
    for filename in files:
        sample = filename.split('/')[-1].split('.')[0]
        with open(filename) as infile:
            for l, line in enumerate(infile):
                
                if method == 'htseq':
                    if not line.startswith('_'):
                        stripped = line.strip('\n')
                        splitted = stripped.split('\t')
                        gene = splitted[0]
                        count = splitted[1]
                        try:
                            counts[sample][gene] = count
                        except KeyError:
                            counts[sample] = {gene: count}

                elif method == 'featurecounts':
                    if not line.startswith('#') and l > 1:
                        stripped = line.strip('\n')
                        splitted = stripped.split('\t')
                        gene = splitted[0]
                        count = splitted[-1]
                        try:
                            counts[sample][gene] = count
                        except KeyError:
                            counts[sample] = {gene: count}

                else:
                    raise RuntimeError("{0} is not a valid method".format(method))

    df = pd.DataFrame(counts)
    return df

def reindex_samples(counts, phenotypes):
    """
    Reorders columns in count matrix based on the
    sample order found in phenotypes file

    Args:
        Param #1 (frame): Pandas dataframe of counts
    Returns:
        Pandas dataframe
    """
    df = pd.read_table(phenotypes).transpose()
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])
    return counts.reindex(columns=list(df.columns))

if __name__ == '__main__':

    if sys.argv[1] == '-p':
        phenotypes = sys.argv[2]
        method     = sys.argv[3]
        files      = sys.argv[4:]
        df = aggregate_counts(files, method)
        df = reindex_samples(df, phenotypes)

    else:
        method     = sys.argv[1]
        files      = sys.argv[2:]
        df = aggregate_counts(files, method)

    df.to_csv('expression_matrix.txt', sep='\t')