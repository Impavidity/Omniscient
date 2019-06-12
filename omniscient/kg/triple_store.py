from omniscient.base.constants import *
from omniscient.base.logger import Log

from elasticsearch import Elasticsearch


logger = Log("info")

class ESTripleStore(object):
  """
  Triple store backend.
  """
  def __init__(self, host, port, settings):
    self.es = Elasticsearch(['{}:{}'.format(host, port)])
    self.settings = settings
    self.index_settings = open(settings[INDEX_SETTINGS]).read()

  def clear_index(self):
    logger.info("removing indices {} ...".format(self.settings[INDEX_NAME]))
    self.es.indices.delete(index=self.settings[INDEX_NAME], ignore=[400, 404])

  def create_index(self):
    logger.info("create indices {}".format(self.settings[INDEX_NAME]))
    self.es.indices.create(index=self.settings[INDEX_NAME], body=self.index_settings[SETTING])
    self.es.indices.put_mapping(index=self.settings[INDEX_NAME], body=self.index_settings[MAPPING], include_type_name=False)

  def add_triple(self, subj, pred, obj):
    pass

