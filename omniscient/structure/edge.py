class Edge(object):

  def __init__(self, id, value):
    self.id = id
    self.value = value

  def __hash__(self):
    return hash(self.id)

  def __eq__(self, other):
    return self.id == other.id

  def __str__(self):
    return f"{self.__class__.__name__}({self.id}: {self.value})"

  __repr__ = __str__