import argparse
import logging
import os
import datetime
import gzip
import spacy
import unicodedata
import json
from sqlitedict import SqliteDict
from multiprocessing import Pool, Lock, Value

from kg.dbpedia.name_extraction import DBPEDIA_FOAF_LONG

FULL_NAME_INDEX = "full_name_inverted_index"
NAME_N_GRAM_INDEX = "name_n_gram_inverted_index"

LOGGER = logging.getLogger("NameExtraction")
LOGGER.setLevel(logging.INFO)

abbre = {"'s", "n't", "'re", "'d", "'ll", "'ve", "'m"}


class AtomicCounter(object):
  def __init__(self):
    self.value = Value("i", 0)
    self.lock = Lock()

  def increment(self):
    with self.lock:
      self.value.value += 1
      return self.value.value


def Triple(uri, string, predicate):
  return {"uri": uri, "string": string, "predicate": predicate}


class InvertedIndex(object):
  model = spacy.load('en', disable=['tagger', 'ner', 'parser'])
  stop_words = model.Defaults.stop_words
  stop_words.update(abbre)
  counter = AtomicCounter()

  def __init__(self, input_path, index_path):
    self.input_path = input_path
    self.index_path = index_path

    LOGGER.info("Input path: " + self.input_path)
    LOGGER.info("Index path: " + self.index_path)

    if not os.path.exists(self.input_path) or not os.path.isfile(self.input_path):
      raise IOError("Input" + self.input_path + " does not exist.")

    if input_path.endswith(".gz"):
      self.f = gzip.open(input_path, 'rb')
    else:
      self.f = open(input_path, 'rb')

    self.full_string_inverted_index = {}
    self.name_n_gram_inverted_index = {}
    self.alias_n_gram_inverted_index = {}

    self.full_collection = SqliteDict(os.path.join(self.index_path, FULL_NAME_INDEX), autocommit=True)
    self.name_collection = SqliteDict(os.path.join(self.index_path, NAME_N_GRAM_INDEX), autocommit=True)

  @staticmethod
  def normalization(val):
    val = val.replace('\\\\', '')
    tokens = InvertedIndex.model(val)
    val = " ".join([token.text for token in tokens])
    lowered = val.lower()
    return lowered

  @staticmethod
  def find_ngrams(input_list, n):
    ngrams = zip(*[input_list[i:] for i in range(n)])
    return set([" ".join(ngram) for ngram in ngrams])

  @staticmethod
  def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

  @staticmethod
  def get_ngram(val):
    # accent folding first
    val = InvertedIndex.strip_accents(val)
    # val is lowered string, because stop_words list are lowercase
    tokens = val.split()
    filtered_tokens = [token for token in tokens if token not in InvertedIndex.stop_words]
    # Remove the stop word and then do the n_gram
    # You need to keep the same style in the lookup
    all_ngrams = set()
    max_n = min(len(filtered_tokens), 3)
    for n in range(1, max_n + 1):
      ngrams = InvertedIndex.find_ngrams(filtered_tokens, n)
      all_ngrams = all_ngrams | ngrams
    return all_ngrams

  @staticmethod
  def process_line(line):
    line = line.decode("utf-8")
    try:
      sub, predicate, obj = json.loads(line)
    except:
      LOGGER.error("[{}] {}".format(datetime.datetime.now(), line))
      exit()
    normalized_obj = InvertedIndex.normalization(obj)
    n_grams = InvertedIndex.get_ngram(normalized_obj)

    count = InvertedIndex.counter.increment()
    if count % 10000 == 0:
      LOGGER.info("[{}] {} strings added.".format(datetime.datetime.now(), count))
    return (sub, predicate, obj, normalized_obj, n_grams)

  def run(self):
    LOGGER.info("[{}] Starting Indexer...".format(datetime.datetime.now()))

    pool = Pool(64)
    results = pool.map(InvertedIndex.process_line, self.f)
    LOGGER.info(
      "[{}] Finish Preprocessing for {} lines".format(datetime.datetime.now(), InvertedIndex.counter.value.value))
    pool.close()
    count = 0
    for sub, predicate, obj, normalized_obj, n_grams in results:
      if predicate not in [DBPEDIA_FOAF_LONG]:
        continue
      if normalized_obj not in self.full_string_inverted_index:
        self.full_string_inverted_index[normalized_obj] = []
      self.full_string_inverted_index[normalized_obj].append(
        Triple(uri=sub, string=obj, predicate=predicate))

      if predicate == DBPEDIA_FOAF_LONG:
        tmp_inverted_index = self.name_n_gram_inverted_index

      for n_gram in n_grams:

        if n_gram not in tmp_inverted_index:
          tmp_inverted_index[n_gram] = []
        tmp_inverted_index[n_gram].append(
          Triple(uri=sub, string=obj, predicate=predicate))

      count += 1
      if count % 10000 == 0:
        LOGGER.info("[{}] {} strings added.".format(datetime.datetime.now(), count))

    LOGGER.info("[{}] Indexing finished. {} strings in total. ".format(datetime.datetime.now(), count))

    LOGGER.info("[{}] Start to writing index to database ...".format(datetime.datetime.now()))
    LOGGER.info("[{}] Stage 1: Write full name index. Total {} index.".format(datetime.datetime.now(),
                                                                              len(self.full_string_inverted_index)))
    count = 0
    for key in self.full_string_inverted_index:
      self.full_collection[key] = self.full_string_inverted_index[key]
      count += 1
      if count % 10000 == 0:
        self.full_collection.commit()
        LOGGER.info("[{}] {} index added.".format(datetime.datetime.now(), count))
    self.full_collection.close()
    del self.full_string_inverted_index
    LOGGER.info("[{}] Close dbs.".format(datetime.datetime.now()))

    LOGGER.info("[{}] Stage 2: Write name index. Total {} index.".format(datetime.datetime.now(),
                                                                         len(self.name_n_gram_inverted_index)))
    count = 0
    for key in self.name_n_gram_inverted_index:
      self.name_collection[key] = self.name_n_gram_inverted_index[key]
      count += 1
      if count % 10000 == 0:
        self.name_collection.commit()
        LOGGER.info("[{}] {} index added.".format(datetime.datetime.now(), count))

    self.name_collection.close()
    del self.name_n_gram_inverted_index
    LOGGER.info("[{}] Close dbs.".format(datetime.datetime.now()))


def main(args):
  InvertedIndex(args.input, args.index).run()


if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--input", type=str, required=True)
  argparser.add_argument("--index", type=str, required=True)
  args = argparser.parse_args()
  main(args)
