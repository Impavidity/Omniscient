import argparse
from jnius import autoclass


class SimpleSearcher(object):
  def __init__(self, path, k1=0.9, b=0.4):
    self.path = path
    self.JString = autoclass('java.lang.String')
    JSearcher = autoclass('io.anserini.search.SimpleSearcher')
    self.searcher = JSearcher(self.JString(path))
    self.searcher.setBM25Similarity(k1, b)

  def query(self, qstring, num=8):
    try:
      hits = self.searcher.search(self.JString(qstring), num)
    except ValueError as e:
      print("Search Error: {}\n{}".format(qstring.encode("utf-8"), e))
      return []

    candidates = []

    for candidate in hits:
      if ("||" in candidate.content) or ("/><" in candidate.content) or \
                    ("|----|" in candidate.content) or ("#fffff" in candidate.content):
        print("################### dirty data #################")
        print(candidate.docid, candidate.ldocid)
      else:
        paragraph_dict = {'text': candidate.content,
                          'paragraph_score': candidate.score,
                          'docid': candidate.docid}
        candidates.append(paragraph_dict)
    return candidates

if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--path", type=str)
  argparser.add_argument("--query", type=str)
  args = argparser.parse_args()
  searcher = SimpleSearcher(path=args.path)
  candidates = searcher.query(qstring=args.query)
  for candidate in candidates:
    print(candidate)