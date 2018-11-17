import argparse
import os
from sqlitedict import SqliteDict

from omniscient.embedding.indexer import EMBEDDING


class Retriever(object):
  def __init__(self, index_path):
    self.index_path = index_path
    self.embedding = SqliteDict(os.path.join(self.index_path, EMBEDDING), flag="r")
    print("Finish Loading")

  def get(self, uri):
    return self.embedding[uri]


def main(args):
  print(Retriever(args.index).get(args.uri))


if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--index", type=str, required=True)
  argparser.add_argument("--uri", type=str, default=None)

  args = argparser.parse_args()
  main(args)
