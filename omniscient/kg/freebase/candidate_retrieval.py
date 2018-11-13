import argparse
import os
from sqlitedict import SqliteDict
import threading

from omniscient.kg.freebase.inverted_index import (
  InvertedIndex,
  FULL_NAME_INDEX,
  NAME_N_GRAM_INDEX,
  ALIAS_N_GRAM_INDEX)


class CandidateRetrieval(object):
  def __init__(self, index_path):
    self.index_path = index_path
    self.full_collection = SqliteDict(os.path.join(self.index_path, FULL_NAME_INDEX), flag="r")
    self.name_collection = SqliteDict(os.path.join(self.index_path, NAME_N_GRAM_INDEX), flag="r")
    self.alias_collection = SqliteDict(os.path.join(self.index_path, ALIAS_N_GRAM_INDEX), flag="r")

    print("Finish Loading")

  def search(self, query, do_ngram=False):
    candidates_full_name = []
    candidates_n_gram = []
    normalize_query = InvertedIndex.normalization(query)
    if normalize_query in self.full_collection:
      candidates_full_name.extend(self.full_collection[normalize_query])
    if do_ngram or len(candidates_full_name) == 0:
      n_grams = sorted(InvertedIndex.get_ngram(normalize_query), key=lambda x: len(x.split()), reverse=True)
      if len(n_grams) > 0:
        max_length = len(n_grams[0].split())
        for n_gram in n_grams:
          cur_length = len(n_gram.split())
          if cur_length < max_length and len(candidates_n_gram) != 0:
            break
          max_length = cur_length
          if n_gram in self.name_collection:
            candidates_n_gram.extend(self.name_collection[n_gram])
          if n_gram in self.alias_collection:
            candidates_n_gram.extend(self.alias_collection[n_gram])
    return candidates_full_name + candidates_n_gram


class SearchThread(threading.Thread):
  def __init__(self, queries):
    threading.Thread.__init__(self)
    self.candidate_retrieval = CandidateRetrieval(args.index_path)
    self.queries = queries

  def run(self):
    print("Start Thread")
    for query in self.queries:
      candidates = self.candidate_retrieval.search(query, args.do_ngram)
      for candidate in candidates:
        print(candidate)


if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--query", type=str, default=None)
  argparser.add_argument("--index_path", type=str, required=True)
  argparser.add_argument("--do_ngram", default=False, action="store_true")
  args = argparser.parse_args()
  thread1 = SearchThread([args.query] * 100)
  thread2 = SearchThread([args.query] * 100)
  thread1.start()
  thread2.start()
  thread1.join()
  thread2.join()
  print('Finish')