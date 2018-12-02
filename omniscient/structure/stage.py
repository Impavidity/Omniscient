from omniscient.serialization.stage_example import StageExample
from omniscient.structure import constant


class Stage(object):

  def __init__(
        self,
        sentence,
        query_graph,
        standpoint,
        variable_pool,
        mention,
        gold_predicate,
        action):
    """

    Args:
      sentence (Sentence):
      query_graph (QueryGraph):
      standpoint (Vertex):
      variable_pool: The variable pool is the state before action
      mention:
      gold_predicate:
      action:
    """
    self.sentence = sentence
    self.query_graph = query_graph
    self.standpoint = standpoint
    self.variable_pool = variable_pool
    self.grounded_variable = None
    self.mention = mention
    self.gold_predicate = gold_predicate
    self.action = action
    self.incoming_edges = None
    self.outgoing_edges = None
    """TODO: The mask function need to be implemented"""
    # self.sentence.mask(self.mention)

  def get_incoming_edges(self, cache=None, utils=None):
    """
    Currently the only resources are cache and QueryGraphUtil
    Args:
      cache:
      utils:
    Returns:

    """
    if self.incoming_edges:
      return self.incoming_edges
    elif cache:
      self.incoming_edges = []
      for standpoint in self.standpoint.grounded_value:
        if standpoint in cache:
          self.incoming_edges.extend(cache[standpoint]["backward_result"])
      return self.incoming_edges
    elif utils:
      self.incoming_edges = []
      for standpoint in self.standpoint.grounded_value:
        self.incoming_edges.extend(utils.retrieve_backward_neighbourhood_with_entity(standpoint))
      return self.incoming_edges
    else:
      raise ValueError("You need to provide resource: Cache or QueryGraphUtil")

  def get_outgoing_edges(self, cache=None, utils=None):
    """

    Args:
      cache:
      utils:

    Returns:

    """
    if self.outgoing_edges:
      return self.outgoing_edges
    elif cache:
      self.outgoing_edges = []
      for standpoint in self.standpoint.grounded_value:
        if standpoint in cache:
          self.outgoing_edges.extend(cache[standpoint]["forward_result"])
      return self.outgoing_edges
    elif utils:
      self.outgoing_edges = []
      for standpoint in self.standpoint.grounded_value:
        self.outgoing_edges.extend(utils.retrieve_forward_neighbourhood_with_entity(standpoint))
      return self.outgoing_edges
    else:
      raise ValueError("You need to provide resource: Cache or QueryGraphUtil")

  def to_training_example(self, cache=None, utils=None):
    examples = []
    for neighbourhood in list(self.get_incoming_edges(cache=cache, utils=utils)
                          + self.get_outgoing_edges(cache=cache, utils=utils)):
      if utils and not utils.is_valid_predicate(neighbourhood["p"]):
        continue
      if neighbourhood['p'] == self.gold_predicate.value:
        continue
      # Not to use the mention for masking for now
      examples.append(StageExample(
        sentence=self.sentence,
        predicate_positive=self.gold_predicate,
        predicate_negative=neighbourhood,
        predicate=constant.NONE,
        gold_predicate=constant.NONE))
    return examples

  def to_testing_example(self, cache=None, utils=None):
    examples = []
    incoming_edges = self.get_incoming_edges(cache=cache, utils=utils)
    outgoing_edges = self.get_outgoing_edges(cache=cache, utils=utils)
    for neighbourhood in incoming_edges + outgoing_edges:
      if utils and not utils.is_valid_predicate(neighbourhood["p"]):
        continue
      examples.append(StageExample(
        sentence=self.sentence,
        predicate_positive=constant.NONE,
        predicate_negative=constant.NONE,
        predicate=neighbourhood,
        gold_predicate=self.gold_predicate))
    return examples

