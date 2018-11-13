import sys, json, re
from collections import defaultdict
input = sys.argv[1]

labels_dict = defaultdict(set)
wd = None
with open(input) as f:
    for line in f:
        line = line.strip()
        if line.startswith("wd:"):
            labels = set()
            wd = re.match("^wd:(.*) rdfs:label",line).group(1)
            # print(wd)
        match = re.match(".*\"(.*)\"@en .*",line)
        if match is not None:
            l = match.group(1)
            # print(l)
            labels_dict[wd].add(l)


with open("wikidata_labels.json", "w") as f:
    for wd, labels in labels_dict.items():
        for l in labels:
            f.write(json.dumps([wd, "rdfs:label", l]) + "\n")

