import pandas as pd
import requests


def main():
    chars = pd.read_csv("../chars.csv")
    haki = pd.read_csv("../haki.csv")

    for _, row in haki.iterrows():
        users = row["users"].split(",")
        for name in users:
            if not (chars["name"] == name).any():
                raise Exception(f"{row['name']} haki user '{name}' not found in chars.csv")

        chars[row["type"].lower()] = chars["name"].isin(users)

    files = chars["name"].apply(lambda name: f"File:{name.replace(' ', '_')}_Portrait.png")

    print(len("|".join(files)))

    chars.to_csv("../full.csv", index=False)


if __name__ == "__main__":
    main()
