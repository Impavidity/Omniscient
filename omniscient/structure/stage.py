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
        action,
        black_predicate_dict):
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
    self.black_predicate_dict = black_predicate_dict
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

  def is_blacked(self, predicate, direction):
    if self.standpoint.value not in self.black_predicate_dict:
      return False
    if (predicate, direction) not in self.black_predicate_dict[self.standpoint.value]:
      return False
    return True

  def to_training_example(self, cache=None, utils=None):
    examples = []
    directions = []
    incoming_edges = self.get_incoming_edges(cache=cache, utils=utils)
    directions.extend([constant.P_BACKWARD] * len(incoming_edges))
    outgoing_edges = self.get_outgoing_edges(cache=cache, utils=utils)
    directions.extend([constant.P_FORWARD] * len(outgoing_edges))
    for neighbourhood, direction in zip(incoming_edges + outgoing_edges, directions):
      if utils and not utils.is_valid_predicate(neighbourhood["p"]):
        continue
      if neighbourhood['p'] == self.gold_predicate.value:
        continue
      if self.is_blacked(neighbourhood['p'], direction):
        continue
      # Not to use the mention for masking for now
      examples.append(StageExample(
        sentence=self.sentence,
        standpoint=self.standpoint,
        predicate_positive=self.gold_predicate,
        predicate_positive_direction=self.action.p_direction,
        predicate_negative=neighbourhood,
        predicate_negative_direction=direction,
        predicate=constant.NONE,
        predicate_direction=constant.NONE,
        gold_predicate=constant.NONE,
        gold_predicate_direction=constant.NONE))
    return examples

  def to_testing_example(self, cache=None, utils=None):
    examples = []
    directions = []
    incoming_edges = self.get_incoming_edges(cache=cache, utils=utils)
    directions.extend([constant.P_BACKWARD] * len(incoming_edges))
    outgoing_edges = self.get_outgoing_edges(cache=cache, utils=utils)
    directions.extend([constant.P_FORWARD] * len(outgoing_edges))
    for neighbourhood, direction in zip(incoming_edges + outgoing_edges, directions):
      if utils and not utils.is_valid_predicate(neighbourhood["p"]):
        continue
      if self.is_blacked(neighbourhood['p'], direction):
        continue
      examples.append(StageExample(
        sentence=self.sentence,
        standpoint=self.standpoint,
        predicate_positive=constant.NONE,
        predicate_positive_direction=constant.NONE,
        predicate_negative=constant.NONE,
        predicate_negative_direction=constant.NONE,
        predicate=neighbourhood,
        predicate_direction=direction,
        gold_predicate=self.gold_predicate,
        gold_predicate_direction=self.action.p_direction))
    return examples

