import pandas as pd
import requests
import json
from itertools import islice, chain
from tqdm import tqdm
from collections import Counter


def batched(iterable, n):
    "Batch data into tuples of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def main():
    chars = pd.read_csv("../chars.csv")
    haki = pd.read_csv("../haki.csv")

    for _, row in haki.iterrows():
        users = row["users"].split(",")
        for name in users:
            if not (chars["name"] == name).any():
                raise Exception(f"{row['name']} haki user '{name}' not found in chars.csv")

        chars[row["type"].lower()] = chars["name"].isin(users)

    files = chars["name"].apply(lambda name: f"File:{name} Portrait.png")

    batches = ["|".join(batch) for batch in batched(files, 50)]
    results = {}
    for batch in tqdm(batches):
        req = requests.get(
            "https://onepiece.fandom.com/api.php",
            params={
                "action": "query",
                "format": "json",
                "formatversion": 2,
                "prop": "imageinfo",
                "iiprop": "url",
                "titles": batch,
            }
        )

        results |= {item["title"]: item["imageinfo"][0]["url"] for item in req.json()["query"]["pages"] if "imageinfo" in item}

    files = files.map(results)
    chars["image"] = files

    chars.to_csv("../full.csv", index=False)


def validate():
    chars = pd.read_csv("../choices.csv").set_index("name")
    importants = chars[["gender", "image", "manga_debut", "height", "affiliation"]]
    nulls = importants.isna().any(axis=1)
    stacked = importants[nulls].stack(dropna=False).reset_index()
    stacked.columns = ["name", "key", "value"]
    stacked = stacked[stacked["value"].isna()].drop("value", axis=1)

    result = pd.merge(chars.reset_index()[["name"]], stacked, on="name", how="right")

    result.to_csv("../nulls.csv", index=False)


def appearances():
    chapters = pd.read_csv("../chapters.csv")
    chapters = chapters["characters"].apply(lambda row: row.split(","))
    counter = Counter(chain(*chapters))

    with open("../appearances.json", "w") as f:
        json.dump(dict(sorted(counter.items(), key=lambda item: -item[1])), f, indent=4, ensure_ascii=False)


def choices():
    with open("../appearance_choices.txt", "r", encoding="utf-8") as f:
        appearance = f.read().splitlines(keepends=False)
    with open("../popular_choices.txt", "r", encoding="utf-8") as f:
        popular = f.read().splitlines(keepends=False)
    chars = pd.read_csv("../full.csv")

    names = set(appearance) | set(popular)
    missing = []
    for name in names:
        if not (chars["name"] == name).any():
            missing.append(name)

    with open("../missing.txt", "w") as f:
        f.write("\n".join(missing))

    choices = chars[chars["name"].isin(names)].copy()

    # I can assume that all the missing choices are male
    # because I've covered all the female characters
    choices["gender"] = choices["gender"].fillna("Male")

    choices.to_csv("../choices.csv", index=False)


if __name__ == "__main__":
    # main()
    # appearances()
    # choices()
    validate()
