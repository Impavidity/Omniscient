class Action(object):

  def __init__(
        self,
        standpoint,
        predicate,
        p_direction,
        action,
        target):
    """
    Args:
      standpoint (Vertex): The observation point
      predicate (Edge): The edge which is associated with this action
      p_direction (constant.P_FORWARD|constant.P_BACKWARD): The direction of the predicate
      action (constant.GEN_VAR|constant.COPY_VAR): The action related to the variable.
        If this action lead to an hidden entity which is visited in previous action, then
        constant.COPY_VAR should be used to represent this hideen entity, denoted with sparql
        variable, which can be inferred in the query step.
        If this action lead to an unseen hidden entity, then constant.GEN_VAR will be used.
      target (Vertex)
    """
    self.standpoint = standpoint
    self.predicate = predicate
    self.p_direction = p_direction
    self.action = action
    self.target = target

  def __str__(self):
    return f"{self.__class__.__name__}({self.standpoint.value}, {self.predicate.value}, {self.p_direction}, {self.action}, {self.target})"

  __repr__ = __str__