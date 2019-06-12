from omniscient.base.constants import *
from omniscient.base.logger import Log

from elasticsearch import Elasticsearch, helpers
import json

logger = Log("info")

class ESTripleStore(object):
  """
  Triple store backend.
  """
  def __init__(self, host, port, settings):
    self.es = Elasticsearch(['{}:{}'.format(host, port)])
    self.settings = settings
    self.index_settings = json.load(open(settings[INDEX_SETTINGS]))
    self.actions = []
    self.triple_number = 1

  def clear_index(self):
    logger.info("removing indices {} ...".format(self.settings[INDEX_NAME]))
    self.es.indices.delete(index=self.settings[INDEX_NAME], ignore=[400, 404])

  def create_index(self):
    logger.info("create indices {}".format(self.settings[INDEX_NAME]))
    self.es.indices.create(index=self.settings[INDEX_NAME], body=self.index_settings[SETTING])
    self.es.indices.put_mapping(index=self.settings[INDEX_NAME], body=self.index_settings[MAPPING], include_type_name=False)

  def add_triple(self, subj, pred, obj):
    self.actions.append({
      "_op_type": "index",
      "_index": self.settings[INDEX_NAME],
      "_source": {
        "subject": {
          "text": subj
        },
        "predicate": {
          "text": pred
        },
        "object": {
          "text": obj
        }
      }
    })
    size = len(self.actions)
    if size >= 100:
      logger.info("Execute bulk load - {} triples. Total: {}".format(
        self.settings[TRIPLES_TO_BULK], self.triple_number))
      helpers.bulk(self.es, self.actions)
      self.actions = []
    self.triple_number += 1

  def close(self):
    helpers.bulk(self.es, self.actions)
    self.actions = []
    logger.info("Execute bulk load - {} triples. Total: {}".format(
      self.settings[TRIPLES_TO_BULK], self.triple_number))

  def search_node(self, node_uri):
    query = {
      "query": {
        "match": {
          "subject.text": node_uri
        }
      },
      "size": 5
    }
    print(query)
    return self.es.search(index=self.settings[INDEX_NAME], body=query)



