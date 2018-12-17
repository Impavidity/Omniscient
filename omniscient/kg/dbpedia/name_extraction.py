# nohup python -u -m kg.freebase.name_extraction \
# --input /tuna1/collections/freebase/freebase-rdf-latest.gz \
# --output_path /tuna1/indexes/kg-index/ \
# --output_file freebase_name.json > freebase_name_extraction.log &

import argparse
import logging
import os
import datetime
import json
from omniscient.kg.dbpedia.dbpedia import DBpedia
from omniscient.kg.dbpedia.dbpedia_node import (
  DBpediaNode,
  DBPEDIA_FOAF_LONG)


LOGGER = logging.getLogger("NameExtraction")
LOGGER.setLevel(logging.INFO)


class StringCollection(object):
  def __init__(self, uri):
    self.uri = uri
    self.names = set([])

  def add_name(self, name):
    self.names.add(name)


class NameExtraction(object):

  def __init__(self, input_dir, output_path, output_file, language_filter):
    self.input_dir = input_dir
    self.output_path = output_path
    self.output_file = output_file
    self.language_filter = language_filter

    LOGGER.info("Input path: " + self.input_dir)
    LOGGER.info("Output path: " + self.output_path)
    LOGGER.info("Output file: " + self.output_file)

    if not os.path.exists(self.input_dir):
      raise IOError("Input" + self.input_dir + " does not exist.")

  def run(self):
    LOGGER.info("[{}] Starting extraction...".format(datetime.datetime.now()))
    if not os.path.exists(self.output_path):
      os.mkdir(self.output_path)
    count = 0
    with open(os.path.join(self.output_path, self.output_file), "w") as fout:
      # for node in DBpedia(self.input_path):
      #   print(node.predicate_values)

      for file in os.listdir(self.input_dir):
        LOGGER.info("Parsing file...{} ".format(file))
        for collection in map(self.parsing_node, DBpedia(os.path.join(self.input_dir,file))):
          for name in collection.names:
            fout.write(json.dumps([collection.uri, DBPEDIA_FOAF_LONG, name]) + "\n")
          count += 1
          if count % 10000 == 0:
            LOGGER.info("[{}] {} nodes added.".format(datetime.datetime.now(), count))
            fout.flush()

      LOGGER.info("[{}] Extraction finished. {} nodes in total. ".format(datetime.datetime.now(), count))

  @staticmethod
  def clean_special_char(val):
    return val.replace("\n", " ").replace("\t", " ").strip()

  def parsing_node(self, src):
    collection = StringCollection(DBpediaNode.clean_uri(src.uri))
    for p in src.predicate_values:
      predicate = DBpediaNode.clean_uri(p)
      if predicate.startswith(DBPEDIA_FOAF_LONG):
        for value in src.predicate_values[p]:
          try:
            obj_val = NameExtraction.clean_special_char(DBpediaNode.normalize_object_value(value, self.language_filter))
            if len(obj_val) > 0:
              collection.add_name(obj_val)
          except:
            LOGGER.error("Cannot parse {}".format(value))
    return collection

def main(args):
  NameExtraction(args.input, args.output_path, args.output_file, json.loads(args.language_filter)).run()


if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--input", type=str, required=True)
  argparser.add_argument("--output_path", type=str, required=True)
  argparser.add_argument("--output_file", type=str, required=True)
  argparser.add_argument("--language_filter", type=str, required=True, default="\"['en']\"")
  args = argparser.parse_args()
  main(args)