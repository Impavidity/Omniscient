import logging

from omniscient.utils.tools import Counter
from omniscient.structure.action import Action
from omniscient.structure.edge import Edge
from omniscient.structure.vertex import Vertex
from omniscient.structure import constant


LOGGER = logging.getLogger("QueryGraph")
LOGGER.setLevel(logging.INFO)

class QueryGraph(object):

  def __init__(
        self,
        query_str=None,
        graph_dict=None,
        reverse_graph_dict=None,
        grounded_results=None):
    """
    Initialize a graph object.
    If no dictionary or None is given, and empty dictionary will be used.
    Attributes:
      graph_dict (:obj:`dict` of :obj:`dict` of :obj:`list` of :obj:`Vertex`):
      subject -> predicate -> [object]
    Args:
      graph_dict (dict[dict[list]]):
    """
    self.query_str = query_str
    if graph_dict and reverse_graph_dict:
      self.graph_dict = graph_dict
      self.reverse_graph_dict = reverse_graph_dict
    else:
      self.graph_dict = {}
      self.reverse_graph_dict = {}
    self.grounded_results = grounded_results
    self.vertex_counter = Counter()
    self.edge_counter = Counter()
    self.id_to_vertex_value = {}
    """dict: map from id to vertex value. For example, 1 -> ?x"""
    self.id_to_edge_value = {}
    """dict: map from id to edge value. For example, 0 -> gender"""
    self.value_to_vertices = {}
    """dict: map from value to Vertex"""
    self.value_to_edges = {}
    """dict: map from value to Edge"""

  def get_vertex(self, value):
    """
    If the value is already in graph, then return the vertex;
      else create the vertex and add it to graph
    Args:
      value (str):
    Returns: Vertex
    """
    if value not in self.value_to_vertices:
      vertex = Vertex(id=self.vertex_counter.get_and_increment(), value=value)
      if self.grounded_results and vertex.type == constant.VARIABLE:
        for result in self.grounded_results:
          vertex.grounding(result[value])
      self.value_to_vertices[vertex.value] = vertex
      self.id_to_vertex_value[vertex.id] = vertex.value
      self.graph_dict[vertex] = {}
      self.reverse_graph_dict[vertex] = {}
    return self.value_to_vertices[value]

  def add_edge(self, value):
    """
    Args:
      value (Tuple(str, str, str)): (subject, predicate, object)
    Returns:
    """
    sub, predicate, obj = value
    if value not in self.value_to_edges:
      edge = Edge(id=self.edge_counter.get_and_increment(), value=predicate)
      self.value_to_edges[edge.id] = edge
      self.id_to_edge_value[edge.id] = edge.value
    else:
      edge = self.value_to_edges[value]
    sub_vertex = self.get_vertex(sub)
    obj_vertex = self.get_vertex(obj)
    if edge not in self.graph_dict[sub_vertex]:
      self.graph_dict[sub_vertex][edge] = []
    if edge not in self.reverse_graph_dict[obj_vertex]:
      self.reverse_graph_dict[obj_vertex][edge] = []
    self.graph_dict[sub_vertex][edge].append(obj_vertex)
    self.reverse_graph_dict[obj_vertex][edge].append(sub_vertex)

  def get_edges(self):
    return self.value_to_edges.values()

  def get_vertices(self):
    return self.value_to_vertices.values()

  def id_to_vertex(self, id):
    return self.value_to_vertices[self.id_to_vertex_value[id]]

  def id_to_edge(self, id):
    return self.value_to_edges[self.id_to_edge_value[id]]

  def value_to_vertex_id(self, value):
    if value in self.value_to_vertices:
      return self.value_to_vertices[value].id
    return None

  def value_to_edge_id(self, value):
    if value in self.value_to_edges:
      return self.value_to_edges[value].id
    return None

  def value_to_vertex(self, value):
    if value in self.value_to_vertices:
      return self.value_to_vertices[value]
    return None

  def value_to_edge(self, value):
    if value in self.value_to_edges:
      return self.value_to_edges[value]
    return None

  def get_adjacent_vertices(self, vertex):
    adjacent_vertices = []
    for edge in self.graph_dict[vertex]:
      adjacent_vertices.extend(self.graph_dict[vertex][edge])
    return set(adjacent_vertices)

  def get_reverse_adjacent_vertices(self, vertex):
    reverse_adjacent_vertices = []
    for edge in self.reverse_graph_dict[vertex]:
      reverse_adjacent_vertices.extend(self.reverse_graph_dict[vertex][edge])
    return set(reverse_adjacent_vertices)

  def undirected_bfs_paths(self, start, goal):
    queue = [(start, [start])]
    while queue:
      (vertex, path) = queue.pop(0)
      for next in self.get_adjacent_vertices(vertex) | self.get_reverse_adjacent_vertices(vertex) - set(path):
        if next == goal:
          yield path + [next]
        else:
          queue.append((next, path + [next]))

  def undirected_shortest_path(self, start, goal):
    """
    Calculate the shortest path between two vertices
    Args:
      start (Vertex): start vertex
      goal (Vertex): goal vertex
    Returns: length (int)
    """
    try:
      return next(self.undirected_bfs_paths(start, goal))
    except StopIteration:
      return None

  def grounding(self, grounded_results=None):
    """
    It is the caller's responsibility to make sure same pair of
      grounded value are in the same index of the `Vertex.grounded_value`
      and `Vertex.norm_grounded_value`
    Args:
      grounded_results:

    Returns:

    """
    if grounded_results:
      self.grounded_results = grounded_results
    elif self.grounded_results is None:
      raise ValueError("Grounded Results should provided")
    try:
      for result in self.grounded_results:
        for var_symbol, value in result.items():
          self.value_to_vertex(f"?{var_symbol}").grounding(value)
    except:
      LOGGER.error("Grouding error")
      LOGGER.error(self.query_str)

  def graph_to_actions(self):
    """
    This function convert the query graph into sequence of actions.
      The algorithm is not deterministic currently.
    Returns: :obj:list of :obj:`Action`
    TODO:
      This the deterministic problem of this algorithm

    """
    actions = []
    """list of Action"""
    visited = {}
    """dict: This ensures that every vertex will be visited only once"""
    queue = []
    """list of Vertex: Processing queue"""
    in_queue = {}
    """dict: True if the Vertex is in queue"""
    generated = {}
    """dict: True if the variable is generated and put into variable pool"""
    for vertex in self.get_vertices():
      in_queue[vertex] = False
      if vertex.type == constant.URI:
        queue.append(vertex)
        visited[vertex] = True
        in_queue[vertex] = True
      elif vertex.type == constant.VARIABLE:
        visited[vertex] = False
        generated[vertex] = False
      else:
        visited[vertex] = False

    while queue:
      vertex = queue.pop(0)
      in_queue[vertex] = False
      # Forward direction
      for edge in self.graph_dict[vertex]:
        for obj in self.graph_dict[vertex][edge]:
          if not visited[obj]:
            queue.append(obj)
            in_queue[obj] = True
            visited[obj] = True
          if not visited[obj] or in_queue[obj]:
            if obj.type == constant.VARIABLE:
              if not generated[obj]:
                variable_action = constant.GEN_VAR
                generated[obj] = True
              else:
                variable_action = constant.COPY_VAR
            else:
              variable_action = constant.ADD_VALUE
            actions.append(
              Action(
                standpoint=vertex,
                predicate=edge,
                p_direction=constant.P_FORWARD,
                action=variable_action,
                target=obj))
      # Backward direction
      for edge in self.reverse_graph_dict[vertex]:
        for sub in self.reverse_graph_dict[vertex][edge]:
          if not visited[sub]:
            queue.append(sub)
            in_queue[sub] = True
            visited[sub] = True
          if not visited[sub] or in_queue[sub]:
            if sub.type == constant.VARIABLE:
              if not generated[sub]:
                variable_action = constant.GEN_VAR
                generated[sub] = True
              else:
                variable_action = constant.COPY_VAR
            else:
              variable_action = constant.ADD_VALUE
            actions.append(
              Action(
                standpoint=vertex,
                predicate=edge,
                p_direction=constant.P_BACKWARD,
                action=variable_action,
                target=sub))
    return actions
