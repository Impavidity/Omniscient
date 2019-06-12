from omniscient.base.logger import Log
from omniscient.base.constants import *

logger = Log("info")

class TripleInjection(object):
  """
  Basic Injection Class. The current backend is elasticsearch
  """
  def __init__(self, settings, triple_store, recreate_index):
    self.settings = settings
    self.triple_store = triple_store
    self.recreate_index = recreate_index

  def run(self):
    if self.recreate_index:
      self.triple_store.clear_index()
      self.triple_store.create_index()
    logger.info("Start Injection ...")

  @staticmethod
  def clean_special_char(val):
    return val.replace("\n", " ").replace("\t", " ").strip()




