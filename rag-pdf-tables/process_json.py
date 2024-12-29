#!/usr/bin/env python

import sys
import json
import pandas as pd
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def flatten_json(data):
    flat_data = {}
    for (head, column) in data.items():
        if isinstance(column, dict):
            for (key, value) in column.items():
                flat_data[f'{head}-{key}'] = value
        else:
            flat_data[head] = column
    return flat_data

def main(args):
    with open(args[0], 'r') as f:
        data = json.load(f)
        flat_data = flatten_json(data)
        # print(json.dumps(flat_data, indent=4))
        df = pd.DataFrame.from_dict(flat_data)
        # convert all columns to numbers using locale.atoi,
        # skipping the first column since it's the header column
        # and first row of the dataframe since it's the header row
        for column in df.columns[1:]:
            df[column] = df[column].apply(locale.atoi)
        if len(args) > 1 and args[1]:
            print(f'Writing to {args[1]}...')
            df.to_parquet(args[1])
        else:
            print(df)

if __name__ == '__main__':
    if len(sys.argv) < 1:
        print(f'Usage: {sys.argv[0]} <json_path> [output_path]')
        sys.exit(1)
    main(sys.argv[1:])
