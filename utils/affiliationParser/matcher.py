import os
import re
import csv
from pathlib import Path
import subprocess
import recordlinkage
from recordlinkage.index import Full

import numpy as np
import pandas as pd
from nltk.tokenize import WhitespaceTokenizer

from .utils import download_grid_data
from .parse import parse_affil, preprocess


path = Path(os.getenv("~", '~/.affliation_parser')).expanduser()
grid_path = (path/"grid")
if not grid_path.exists():
    download_grid_data()
grid_df = pd.read_csv(grid_path/"grid.csv", header=0,
                      names=["grid_id", "institution", "city", "state", "country"])
grid_df["location"] = grid_df.city + " " + grid_df.state


def match_affil(affiliation: str, k: int = 1):
    """
    Match affliation to GRID dataset.
    Return a da
    """
    parsed_affil = parse_affil(affiliation)
    print(parsed_affil)
    df = pd.DataFrame([parsed_affil])

    indexer = recordlinkage.Index()
    indexer.add(Full())
    candidate_links = indexer.index(df, grid_df)

    # recordlinkage comparer
    compare = recordlinkage.Compare()
    compare.exact("institution", "institution")
    compare.string("location", "location", method="jarowinkler")
    compare.string("country", "country", method="jarowinkler")

    features_df = compare.compute(candidate_links, df, grid_df)
    features_df["score"] = np.average(features_df, axis=1, weights=[0.6, 0.2, 0.2])

    topk_df = features_df[["score"]].reset_index().sort_values("score", ascending=False).head(k)
    topk_df = topk_df.merge(grid_df.reset_index(), left_on="level_1", right_on="index").\
        drop(labels=["level_0", "level_1", "location"], axis=1)

    return topk_df.to_dict(orient="records")
