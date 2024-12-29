#!/usr/bin/env python

import json
import locale
import sys

import pandas as pd

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

TRANSLATION_MAP_HEADERS = {
    "都道府県": "Prefecture",
    "第二種免許-大型": "Second Class License - Large",
    "第二種免許-中型": "Second Class License - Medium",
    "第二種免許-普通": "Second Class License - Ordinary",
    "第二種免許-大型特殊": "Second Class License - Large Special",
    "第二種免許-牽引": "Second Class License - Towing",
    "第二種免許-小計": "Second Class License - Subtotal",
    "第一種免許-大型": "First Class License - Large",
    "第一種免許-中型": "First Class License - Medium",
    "第一種免許-準中型": "First Class License - Semi-Medium",
    "第一種免許-普通": "First Class License - Ordinary",
    "第一種免許-大型特殊": "First Class License - Large Special",
    "第一種免許-大型二輪": "First Class License - Large Two-Wheel",
    "第一種免許-普通二輪": "First Class License - Ordinary Two-Wheel",
    "第一種免許-小型特殊": "First Class License - Small Special",
    "第一種免許-原付": "First Class License - Moped",
    "第一種免許-小計": "First Class License - Subtotal",
    "合計": "Total",
    "年齢": "Age",
}

TRANSLATION_MAP_PREFECTURES = {
    "北海道": "Hokkaido",
    "青森県": "Aomori",
    "岩手県": "Iwate",
    "宮城県": "Miyagi",
    "秋田県": "Akita",
    "山形県": "Yamagata",
    "福島県": "Fukushima",
    "警視庁": "Tokyo",
    "茨城県": "Ibaraki",
    "栃木県": "Tochigi",
    "群馬県": "Gunma",
    "埼玉県": "Saitama",
    "千葉県": "Chiba",
    "神奈川県": "Kanagawa",
    "新潟県": "Niigata",
    "山梨県": "Yamanashi",
    "長野県": "Nagano",
    "静岡県": "Shizuoka",
    "富山県": "Toyama",
    "石川県": "Ishikawa",
    "福井県": "Fukui",
    "岐阜県": "Gifu",
    "愛知県": "Aichi",
    "三重県": "Mie",
    "滋賀県": "Shiga",
    "京都府": "Kyoto",
    "大阪府": "Osaka",
    "兵庫県": "Hyogo",
    "奈良県": "Nara",
    "和歌山県": "Wakayama",
    "鳥取県": "Tottori",
    "島根県": "Shimane",
    "岡山県": "Okayama",
    "広島県": "Hiroshima",
    "山口県": "Yamaguchi",
    "徳島県": "Tokushima",
    "香川県": "Kagawa",
    "愛媛県": "Ehime",
    "高知県": "Kochi",
    "福岡県": "Fukuoka",
    "佐賀県": "Saga",
    "長崎県": "Nagasaki",
    "熊本県": "Kumamoto",
    "大分県": "Oita",
    "宮崎県": "Miyazaki",
    "鹿児島県": "Kagoshima",
    "沖縄県": "Okinawa",
    "合 計": "Total",
}


def flatten_json(data):
    flat_data = {}
    for head, column in data.items():
        if isinstance(column, dict):
            for key, value in column.items():
                flat_data[f"{head}-{key}"] = value
        else:
            flat_data[head] = column
    return flat_data


def translate_column_names(df: pd.DataFrame):
    df = df.rename(columns=TRANSLATION_MAP_HEADERS)
    return df


def translate_prefectures(df: pd.DataFrame):
    df[df.columns[0]] = df[df.columns[0]].map(TRANSLATION_MAP_PREFECTURES)


def main(args):
    with open(args[0], "r") as f:
        data = json.load(f)
        flat_data = flatten_json(data)
        # print(json.dumps(flat_data, indent=4))
        df = pd.DataFrame.from_dict(flat_data)
        # convert all columns to numbers using locale.atoi,
        # skipping the first column since it's the header column
        # and first row of the dataframe since it's the header row
        for column in df.columns[1:]:
            df[column] = df[column].apply(locale.atoi)
        # the first column header is invalid format (like 種類\n年齢)
        # so we need to split it and use the second part as the new header
        try:
            df = df.rename(columns={df.columns[0]: df.columns[0].split("\n")[1]})
        except IndexError:
            pass
        df = translate_column_names(df)
        if df.columns[0] == "Prefecture":
            translate_prefectures(df)
        if len(args) > 1 and args[1]:
            print(f"Writing to {args[1]}...")
            df.to_parquet(args[1])
        else:
            print(df)


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print(f"Usage: {sys.argv[0]} <json_path> [output_path]")
        sys.exit(1)
    main(sys.argv[1:])
