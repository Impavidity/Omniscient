# nohup python -u -m kg.freebase.name_extraction \
# --input /tuna1/collections/freebase/freebase-rdf-latest.gz \
# --output_path /tuna1/indexes/kg-index/ \
# --output_file freebase_name.json > freebase_name_extraction.log &

import argparse
import logging
import os
import datetime
import json

from omniscient.kg.freebase.freebase import Freebase
from omniscient.kg.freebase.freebase_node import FreebaseNode, FREEBASE_NS_SHORT


FB_OBJECT_NAME = FREEBASE_NS_SHORT + "type.object.name"
FB_COMMON_TOPIC_ALIAS =  FREEBASE_NS_SHORT + "common.topic.alias"

LOGGER = logging.getLogger("NameExtraction")
LOGGER.setLevel(logging.INFO)

class StringCollection(object):
  def __init__(self, mid):
    self.mid = mid
    self.names = set([])
    self.aliases = set([])

  def add_name(self, name):
    self.names.add(name)

  def add_alias(self, alias):
    self.aliases.add(alias)

class NameExtraction(object):

  def __init__(self, input_path, output_path, output_file):
    self.input_path = input_path
    self.output_path = output_path
    self.output_file = output_file

    LOGGER.info("Input path: " + self.input_path)
    LOGGER.info("Output path: " + self.output_path)
    LOGGER.info("Output file: " + self.output_file)

    if not os.path.exists(self.input_path) or not os.path.isfile(self.input_path):
      raise IOError("Input" + self.input_path + " does not exist.")

  def run(self):
    LOGGER.info("[{}] Starting extraction...".format(datetime.datetime.now()))
    if not os.path.exists(self.output_path):
      os.mkdir(self.output_path)
    count = 0
    with open(os.path.join(self.output_path, self.output_file), "w") as fout:
      for collection in map(self.parsing_node, Freebase(self.input_path)):
        for name in collection.names:
          fout.write(json.dumps([collection.mid, FB_OBJECT_NAME, name]) + "\n")
        for alias in collection.aliases:
          fout.write(json.dumps([collection.mid, FB_COMMON_TOPIC_ALIAS, alias]) + "\n")
        count += 1
        if count % 2000000 == 0:
          LOGGER.info("[{}] {} nodes added.".format(datetime.datetime.now(), count))
          fout.flush()

      LOGGER.info("[{}] Extraction finished. {} nodes in total. ".format(datetime.datetime.now(), count))

  @staticmethod
  def clean_special_char(val):
    return val.replace("\n", " ").replace("\t", " ").strip()

  def parsing_node(self, src):
    collection = StringCollection(FreebaseNode.clean_uri(src.uri))
    for p in src.predicate_values:
      predicate = FreebaseNode.clean_uri(p)
      if predicate.startswith(FB_OBJECT_NAME):
        for value in src.predicate_values[p]:
          obj_val = NameExtraction.clean_special_char(FreebaseNode.normalize_object_value(value))
          if len(obj_val) > 0:
            collection.add_name(obj_val)
      elif predicate.startswith(FB_COMMON_TOPIC_ALIAS):
        for value in src.predicate_values[p]:
          obj_val = NameExtraction.clean_special_char(FreebaseNode.normalize_object_value(value))
          if len(obj_val) > 0:
            collection.add_alias(obj_val)
    return collection

def main(args):
  NameExtraction(args.input, args.output_path, args.output_file).run()


if __name__ == "__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--input", type=str, required=True)
  argparser.add_argument("--output_path", type=str, required=True)
  argparser.add_argument("--output_file", type=str, required=True)
  args = argparser.parse_args()
  main(args)