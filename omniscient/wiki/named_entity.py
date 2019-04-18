import glob
import bz2
import json
from tqdm import tqdm
import click


@click.group()
def cli():
  pass

@click.command()
@click.option("--file_path")
def extract_named_entity(file_path):
  collections = glob.glob(file_path + '/*/*.bz2', recursive=True)
  examples = []
  for file in tqdm(collections):
    with bz2.open(file, "rt") as fin:
      for line in fin:
        example = json.loads(line)
        examples.append(example)


