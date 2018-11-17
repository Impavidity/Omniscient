import argparse
import datetime
import logging
from sqlitedict import SqliteDict
import numpy as np
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EmbeddingIndexer")
EMBEDDING = "embbeding_index"


class EmbeddingIndexer(object):
  def __init__(self, embedding_file, index_file):
    self.embedding_file = embedding_file
    self.index_file = index_file
    logger.info("Input path: " + self.embedding_file)
    logger.info("Index path: " + self.index_file)
    self.embedding = SqliteDict(os.path.join(self.index_file, EMBEDDING), autocommit=True)

  def iterator(self):
    with open(self.embedding_file) as f:
      for line in f:
        tokens = line.strip().split(" ")
        if len(tokens) == 2:
          continue
        uri = tokens[0]
        embedding = np.array(tokens[1:], dtype=np.float32)
        yield (uri, embedding)

  def run(self):
    count = 0
    for key, value in self.iterator():
      self.embedding[key] = value
      count += 1
      if count % 20000 == 0:
        self.embedding.commit()
        logger.info("[{}] {} index added.".format(datetime.datetime.now(), count))
    self.embedding.close()


def main(args):
  EmbeddingIndexer(args.input, args.index).run()


if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--input", type=str, required=True)
  argparser.add_argument("--index", type=str, required=True)
  args = argparser.parse_args()
  main(args)
