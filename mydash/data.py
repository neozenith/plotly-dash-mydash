"""Data Management functions for dashboard."""

# Standard Library
import json
import os
import pathlib
from types import GeneratorType
from typing import Any, Dict, List

# Third Party Libraries
import pandas as pd


def list_assets(datapath):
    """Generate list of jsonline files discovered from datapath and grouped by their folder."""
    for k, v in groupby(list_files(datapath), lambda x: x[1]).items():
        yield k, v


def get_dataframes(jsonl_files):
    """Generate DataFrames from list of jsonl files."""
    # load_jsonl - For each folder group load and concatenate the jsonlines
    # flatten_json_leaves - flatten all key paths to leaf values into individual records
    # groupby - identical keypaths (json_stem_key) and map to dict (json_stem_to_record)
    jsonl_grouped_records = groupby(
        flatten_json_leaves(load_jsonl(jsonl_files)), _json_stem_key, _json_stem_to_record
    )

    for _k, _v in jsonl_grouped_records.items():

        # Now each JSON document could have many DataFrames yielded based
        # on the unique combination of keypaths creating distinct dataschemas
        df = pd.DataFrame.from_dict(_v)
        yield {"record_path": _k, "data": df}


def list_files(datapath):
    """Given a path, recurse and find all JSON files.

    Returns a tuple of (datapath, rest_of_path, filename) so that multiple files
    can be grouped by the rest_of_path but joining all three tuple components gives
    a full path to load data.
    """
    for root, dirs, files in os.walk(datapath):
        for file in files:
            if file.endswith(".json"):
                yield (datapath, root.replace(datapath, ""), file)


def groupby(iterator, group_fun, map_fun=None):
    """Generate a dict from an iterable, using group_fun to specify the grouping key."""
    output: Dict[str, List[Any]] = {}
    for v in iterator:
        k = group_fun(v)
        _v = map_fun(v) if map_fun else v
        if k in output:
            output[k].append(_v)
        else:
            output[k] = [_v]
    return output


def load_jsonl(files):
    """Read a list of filepaths which each contain jsonlines.

    Return a list of JSON as though all files where one jsonl file.
    """
    for f in files:
        filename = pathlib.Path(f[0]) / pathlib.Path(f[1]) / pathlib.Path(f[2])
        with open(filename) as file:
            for line in file:
                yield json.loads(line)


def flatten_json_leaves(json_obj):
    """Traverse JSON tree to return a table of leaves."""
    # Handle the case where the root document is coming from jsonl generator
    _json_obj = json_obj
    if isinstance(json_obj, GeneratorType):
        try:
            _json_obj = next(json_obj)
        except StopIteration:
            return

    if type(_json_obj) == dict:
        for k, v in _json_obj.items():
            for item in flatten_json_leaves(v):
                yield [k, *item] if type(item) == list else [k, item]

    elif type(_json_obj) == list:
        list_length = len(_json_obj)  # min(2, len(json_obj))
        for i, v in enumerate(_json_obj[:list_length]):
            for item in flatten_json_leaves(v):
                yield [i, *item] if type(item) == list else [i, item]

    else:
        yield _json_obj


def _json_stem_key(json_stem):
    keypath = [x for x in json_stem[:-2] if type(x) == str]
    key_val = [type(x).__name__ for x in json_stem[-2:]]
    return ".".join(keypath + key_val)


def _json_stem_to_record(json_stem):
    output = {"key": json_stem[-2], "value": json_stem[-1]}
    accumulative_key = []
    for i, v in enumerate(json_stem[:-2]):
        if i == 0 and type(v) == int:
            output["docId"] = v
        elif type(v) == str:
            accumulative_key.append(v)
        else:
            output[".".join(accumulative_key)] = v
            accumulative_key = []

    return output
