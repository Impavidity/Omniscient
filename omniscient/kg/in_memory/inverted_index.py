import argparse
import logging
import os
from multiprocessing import Pool
import datetime
import json
import gzip
from re import compile as _Re
import pickle

from omniscient.utils.tools import AtomicCounter


LOGGER = logging.getLogger("In-Memory-Indexing")
LOGGER.setLevel(logging.INFO)


_unicode_chr_splitter = _Re( '(?s)((?:[\ud800-\udbff][\udc00-\udfff])|.)' ).split
def split_unicode_chrs( text ):
  return [ chr for chr in _unicode_chr_splitter( text ) if chr ]


def find_ngrams(input_list, n):
  ngrams = zip(*[input_list[i:] for i in range(n)])
  return set(["".join(ngram) for ngram in ngrams])


def get_ngram_zh(val):
  tokens = split_unicode_chrs(val)
  n = min(len(tokens), 2)
  ngrams = find_ngrams(tokens, n)
  return ngrams


def process_line_zh(line):
  line = line.decode("utf-8")
  try:
    sub, predicate, obj = json.loads(line)
  except:
    LOGGER.error("[{}] {}".format(datetime.datetime.now(), line))
    exit()
  n_grams = get_ngram_zh(obj)
  InvertedIndex.counter.increment()
  return (sub, predicate, obj, n_grams)

processor_func_dict = {
  "zh": process_line_zh
}

def Triple(mid, string, predicate):
  return {"mid": mid, "string": string, "predicate": predicate}

class InvertedIndex(object):
  counter = AtomicCounter()

  def __init__(self, input_path, index_path, processor):
    self.input_path = input_path
    self.index_path = index_path
    self.processor = processor

    LOGGER.info("Input path: " + self.input_path)
    LOGGER.info("Index path: " + self.index_path)
    LOGGER.info("Processor function: " + self.processor)

    if not os.path.exists(self.input_path) or not os.path.isfile(self.input_path):
      raise IOError("Input" + self.input_path + " does not exist.")

    self.inverted_index = {}

    if input_path.endswith(".gz"):
      self.f = gzip.open(input_path, 'rb')
    else:
      self.f = open(input_path, 'rb')

  def run(self):
    LOGGER.info("[{}] Starting Indexer...".format(datetime.datetime.now()))

    pool = Pool(3)
    results = pool.map(processor_func_dict[self.processor], self.f)

    LOGGER.info(
      "[{}] Finish Preprocessing for {} lines".format(datetime.datetime.now(), InvertedIndex.counter.value.value))
    pool.close()
    count = 0
    for sub, predicate, obj, n_grams in results:
      if obj not in self.inverted_index:
        self.inverted_index[obj] = []
      self.inverted_index[obj].append(
        Triple(mid=sub, string=obj, predicate=predicate))
      for n_gram in n_grams:
        if n_gram not in self.inverted_index:
          self.inverted_index[n_gram] = []
        self.inverted_index[n_gram].append(
          Triple(mid=sub, string=obj, predicate=predicate))
      count += 1
      if count % 100000 == 0:
        LOGGER.info("[{}] {} strings added.".format(datetime.datetime.now(), count))
    pickle.dump(self.inverted_index, open(self.index_path, "wb"))


def main(args):
  InvertedIndex(args.input, args.index, args.processor).run()


if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--input", type=str, required=True)
  argparser.add_argument("--index", type=str, required=True)
  argparser.add_argument("--processor", type=str, required=True)
  args = argparser.parse_args()
  main(args)