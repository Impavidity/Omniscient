import argparse
import os
from sqlitedict import SqliteDict

from kg.freebase.inverted_index import (
  InvertedIndex,
  FULL_NAME_INDEX,
  NAME_N_GRAM_INDEX,
  ALIAS_N_GRAM_INDEX)


class CandidateRetrieval(object):
  def __init__(self, index_path):
    self.index_path = index_path
    self.full_collection = SqliteDict(os.path.join(self.index_path, FULL_NAME_INDEX))
    self.name_collection = SqliteDict(os.path.join(self.index_path, NAME_N_GRAM_INDEX))
    self.alias_collection = SqliteDict(os.path.join(self.index_path, ALIAS_N_GRAM_INDEX))

    print("Finish Loading")

  def search(self, query, do_ngram=True):
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


def main():
  pass


def test():
  pass


if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--query", type=str, default=None)
  argparser.add_argument("--index_path", type=str, required=True)
  args = argparser.parse_args()
  candidate_retrieval = CandidateRetrieval(args.index_path)
  candidates = candidate_retrieval.search(args.query)
  for candidate in candidates:
    print(candidate)
