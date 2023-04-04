#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2021-2023 Stephen Kraus
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path
import csv
import os
import shutil
import json
import uuid


def row_to_jlpt_term(row, level):
    (_, kanji, kana, _, origin, original) = row
    freq_value = level
    if origin == "waller":
        freq_display = f"N{level}"
    elif origin == "jmdict":
        freq_display = f"N{level} ({original})"
    else:
        raise Exception(f"Unexpected 'origin' in N{level} data: '{origin}'")
    if kanji != "":
        term = [
            kanji,
            "freq",
            {
                "reading": kana,
                "frequency": {
                    "value": freq_value,
                    "displayValue": freq_display
                }
            }
        ]
    else:
        term = [
            kana,
            "freq",
            {
                "value": freq_value,
                "displayValue": freq_display
            }
        ]
    return term


def load_csv(filename):
    csv_data = []
    with open(filename) as csv_file:
        first = True
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if first:  # skip first row (headers)
                first = False
                continue
            csv_data.append(row)
    return csv_data


def make_jlpt_terms():
    terms = []
    for jlpt_level in [5, 4, 3, 2, 1]:
        filename = f"n{jlpt_level}.csv"
        csv_data = load_csv(filename)
        for row in csv_data:
            term = row_to_jlpt_term(row, jlpt_level)
            terms.append(term)
    return terms


def write_term_meta_dictionary(terms, filename, index):
    output_dir = str(uuid.uuid4())
    os.mkdir(output_dir)

    terms_per_file = 4000
    max_i = int(len(terms) / terms_per_file) + 1
    for i in range(max_i):
        term_file = f"{output_dir}/term_meta_bank_{i+1}.json"
        with open(term_file, "w", encoding='utf8') as f:
            start = terms_per_file * i
            end = terms_per_file * (i + 1)
            json.dump(terms[start:end], f, indent=4, ensure_ascii=False)

    with open(f"{output_dir}/index.json", 'w') as f:
        json.dump(index, f, indent=4, ensure_ascii=False)

    if Path(f"{filename}.zip").is_file():
        os.remove(f"{filename}.zip")

    shutil.make_archive(filename, 'zip', output_dir)
    shutil.rmtree(output_dir)


if __name__ == '__main__':
    terms = make_jlpt_terms()
    filename = "jlpt"
    index = {
        "revision": "JLPT;2022-01-30",
        "description": "https://github.com/stephenmk/yomichan-jlpt-vocab",
        "title": "JLPT",
        "format": 3,
        "author": "stephenmk",
    }
    write_term_meta_dictionary(terms, filename, index)
