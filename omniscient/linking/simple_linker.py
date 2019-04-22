import argparse
from typing import Dict


from omniscient.kg.freebase.candidate_retrieval import CandidateRetrieval as FreebaseRetriever
from omniscient.kg.dbpedia.candidate_retrieval import CandidateRetrieval as DBpediaRetriever
from omniscient.kg.wikidata.candidate_retrieval import CandidateRetrieval as WikidataRetriever

def get_retriever(backend, index_path):
  if backend.lower() == "freebase":
    return FreebaseRetriever(index_path=index_path)
  if backend.lower() == "dbpedia":
    return DBpediaRetriever(index_path=index_path)
  if backend.lower() == "wikidata":
    return WikidataRetriever(index_path=index_path)

class EntityLinker(object):
  """
  This is an simple implementation of entity linker for agile development.
  Basic idea is to use string matching, string similarity score, etc. to
    do the entity linking.
  """
  def __init__(self, backends: Dict):
    self.retrievers = {}
    self.backends = backends
    for backend, index_path in backends.items():
      self.retrievers[backend] = get_retriever(backend, index_path)

  def link(self, mention: str) -> Dict:
    results = {}
    for backend in self.backends.keys():
      results[backend] = self.retrievers[backend].search(mention, mode="optimal")
    return results

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  linker = EntityLinker({
    "freebase": "/tuna1/indexes/s-freebase",
    "dbpedia": "/tuna1/indexes/s-dbpedia",
    "wikidata": "/tuna1/indexes/s-wikidata"})
  while True:
    query = input("Input Mention: ")
    results = linker.link(query)
    print(results)

