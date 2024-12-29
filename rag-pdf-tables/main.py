#!/usr/bin/env python

import sys
import json
import pdfplumber

args = sys.argv[1:]

if len(args) < 2:  # Check if the user has provided the required arguments
    print('Usage: python main.py <pdf_file_path> <output_folder>')
    sys.exit(1)

def get_col(rows, col):
    return [row[col] for row in rows]

def has_merged_cells(row, start_col, end_col):
    null_indexes = [i for i, cell in enumerate(row[start_col:end_col]) if cell is None]
    if len(null_indexes) >= 1:
        if len(null_indexes) == 1 and null_indexes[0] == 0:
            return False
        return True
    return False

def build_json(rows, start_col, end_col):
    repr_data = {}
    last_header_idx = 0
    while has_merged_cells(rows[last_header_idx + 1], start_col, end_col):
        last_header_idx += 1
    # print(f'[{len(rows)}, {start_col}, {end_col}] Last header index: {last_header_idx}')
    row = rows[0]
    j = start_col
    while j < end_col:
        cell = row[j]
        k = j
        while last_header_idx > 0 and k < end_col - 1 and row[k + 1] is None:
            k += 1
        if k > j:
            repr_data[cell] = build_json(rows[1:], j, k + 1)
        else:
            repr_data[cell] = get_col(rows[last_header_idx + 1:], j)
        j = k + 1
    return repr_data

def main():
    fpath = args[0]
    pdfname = fpath.split('/')[-1].split('.')[0]
    output_folder = args[1]
    with pdfplumber.open(fpath) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            repr_data = {}
            if table is not None:
                print(f'Page {page.page_number} has a table')
                print(table[:3])
                print('Building JSON...')
                table_json = build_json(table, 0, len(table[0]))
                with open(f'{output_folder}/{pdfname}_page{page.page_number}.json', 'w') as f:
                    json.dump(table_json, f, indent=4)

if __name__ == '__main__':
    main()
