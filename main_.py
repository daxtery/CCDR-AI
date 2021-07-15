from ccdr.transformers.equipment_transformer import stringuify

import json

from pprint import pprint

if __name__ == "__main__":
    with open("examples.json", "r") as f:
        data = json.load(f)
        for d in data:
            print()
            pprint(stringuify(d))
            print()