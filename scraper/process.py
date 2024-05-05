import pandas as pd
import requests
from itertools import islice
from tqdm import tqdm


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
    chars = pd.read_csv("../full.csv")
    missing = set(chars[
        chars["image"].isna()
        | chars["manga_debut"].isna()
    ]["name"])

    with open("../missing.txt", "w") as f:
        f.write("\n".join(missing))


if __name__ == "__main__":
    main()
    validate()
