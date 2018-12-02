import pytest

from omniscient.structure.query_graph import QueryGraph


class TestQueryGraph(object):
  def test_get_vertex(self):
    query_graph = QueryGraph()
    vertex_variable = query_graph.get_vertex("?c")
    assert vertex_variable.id == 0
    assert vertex_variable.value == "?c"

  def test_grounding(self):
    query_graph = QueryGraph()
    query_graph.add_edge((
      "?c",
      "http://rdf.freebase.com/ns/location.country.administrative_divisions",
      "http://rdf.freebase.com/ns/m.010vz"))
    grounded_results = [
      {"?c": "http://rdf.freebase.com/ns/m.060c4"},
      {"?c": "http://rdf.freebase.com/ns/m.3xy95"}]
    query_graph.grounding(grounded_results=grounded_results)
    vertex = query_graph.get_vertex("?c")
    assert vertex.norm_grounded_value == ["ns:m.060c4", "ns:m.3xy95"]

  def test_graph_to_actions(self):
    query_graph = QueryGraph()
    query_graph.add_edge((
      "?c",
      "http://rdf.freebase.com/ns/location.country.administrative_divisions",
      "http://rdf.freebase.com/ns/m.010vz"))
    query_graph.add_edge((
      "?c",
      "http://rdf.freebase.com/ns/government.governmental_jurisdiction.governing_officials",
      "?y"))
    query_graph.add_edge((
      "?y",
      "http://rdf.freebase.com/ns/government.government_position_held.office_holder",
      "?x"))
    query_graph.add_edge((
      "?y",
      "http://rdf.freebase.com/ns/government.government_position_held.basic_title",
      "http://rdf.freebase.com/ns/m.060c4"))
    actions = query_graph.graph_to_actions()
    assert len(actions) == 4

