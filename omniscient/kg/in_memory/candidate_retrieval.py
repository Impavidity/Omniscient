import argparse
import pickle

class CandidateRetrieval(object):
  def __init__(self, index_path):
    self.index_path = index_path
    self.inverted_index = pickle.load(open(self.index_path, 'rb'))
    print("finish loading")

  def search(self, query):
    return self.inverted_index.get(query, [])


if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--query", type=str, default=None)
  argparser.add_argument("--index_path", type=str, required=True)
  args = argparser.parse_args()
  candidate_retrieval = CandidateRetrieval(args.index_path)
  print(candidate_retrieval.search(args.query))