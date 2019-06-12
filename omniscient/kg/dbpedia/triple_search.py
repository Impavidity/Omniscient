from elasticsearch import Elasticsearch
from omniscient.kg.triple_store import ESTripleStore
import argparse
from omniscient.base.constants import INDEX_NAME, INDEX_SETTINGS

class DBpediaTripleSearcher(object):
  def __init__(self, triple_store):
    self.triple_store = triple_store

  def search_node(self, node_uri):
    results = self.triple_store.search_node(node_uri)
    print(results)


def main(args):
  settings = {
    INDEX_NAME: "dbpedia_triple",
    INDEX_SETTINGS: args.config_file
  }
  es_triple_store = ESTripleStore(args.host, args.port, settings)
  DBpediaTripleSearcher(triple_store=es_triple_store).search_node("http://dbpedia.org/resource/Actrius")

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--config_file")
  parser.add_argument("--host")
  parser.add_argument("--port")
  args = parser.parse_args()
  main(args)