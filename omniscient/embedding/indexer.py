import argparse
import datetime
import logging
from sqlitedict import SqliteDict


LOGGER = logging.getLogger("EmbeddingIndexer")
LOGGER.setLevel(logging.INFO)

class EmbeddingIndexer(object):
  def __init__(self, embedding_file, index_file):
    self.embedding_file = embedding_file
    self.index_file = index_file
    LOGGER.info("Input path: " + self.embedding_file)
    LOGGER.info("Index path: " + self.index_file)
    self.embedding = SqliteDict(self.index_file, autocommit=True)

  def iterator(self):
    raise NotImplementedError

  def run(self):
    count = 0
    for key, value in self.iterator():
      self.embedding[key] = value
      count += 1
      if count % 20000:
        self.embedding.commit()
        LOGGER.info("[{}] {} index added.".format(datetime.datetime.now(), count))
    self.embedding.close()