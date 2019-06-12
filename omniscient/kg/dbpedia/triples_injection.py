import os
import argparse

from omniscient.base.logger import Log
from omniscient.base.constants import *
from omniscient.kg.triples_injection import TriplesInjection
from omniscient.kg.triple_store import ESTripleStore
from omniscient.kg.dbpedia.dbpedia import DBpedia
from omniscient.kg.dbpedia.dbpedia_node import DBpediaNode

logger = Log("info")

class DBpediaTriplesInjection(TriplesInjection):
  def __init__(self, settings, triple_store, recreate_index):
    super(DBpediaTriplesInjection, self).__init__(settings, triple_store, recreate_index)

  def run(self):
    # super(DBpediaTriplesInjection, self).run()
    input_dir = self.settings[INPUT_DIR]
    for file in os.listdir(self.settings[INPUT_DIR]):
      logger.info("Parsing file {} ...".format(file))
      for src in DBpedia(os.path.join(input_dir, file)):
        subj = DBpediaNode.clean_uri(src.uri)
        for p in src.predicate_values:
          predicate = DBpediaNode.clean_uri(p)
          for value in src.predicate_values[p]:
            try:
              obj_val = TriplesInjection.clean_special_char(
                DBpediaNode.normalize_object_value(value, None))
              if len(obj_val) > 0:
                self.triple_store.add_triple(subj, predicate, obj_val)
            except:
              logger.info("Cannot parse {}".format(value))

def main(args):
  settings = {
    INPUT_DIR: args.input_dir,
    INDEX_SETTINGS: args.config_file,
    INDEX_NAME: "dbpedia_triple"
  }
  triple_store = ESTripleStore(args.host, args.port, settings)
  DBpediaTriplesInjection(settings, triple_store, True).run()

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--input_dir")
  parser.add_argument("--config_file")
  parser.add_argument("--host")
  parser.add_argument("--port")
  args = parser.parse_args()
  main(args)