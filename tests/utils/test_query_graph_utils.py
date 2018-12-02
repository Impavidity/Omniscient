import pytest

from omniscient.utils.query_graph_utils import QueryGraphUtils


@pytest.fixture(scope="class")
def setup():
  sparql = """
      PREFIX ns: <http://rdf.freebase.com/ns/>
      SELECT DISTINCT ?x
      WHERE {
        FILTER (?x != ?c)
        FILTER (!isLiteral(?x) OR lang(?x) = '' OR langMatches(lang(?x), 'en'))
        ?c ns:location.country.administrative_divisions ns:m.010vz . 
        ?c ns:government.governmental_jurisdiction.governing_officials ?y .
        ?y ns:government.government_position_held.office_holder ?x .
        ?y ns:government.government_position_held.basic_title ns:m.060c4 .
        FILTER(NOT EXISTS {?y ns:government.government_position_held.from ?sk0} || 
        EXISTS {?y ns:government.government_position_held.from ?sk1 . 
        FILTER(xsd:gYear(?sk1) <= \"1980\"^^xsd:gYear) })
        FILTER(NOT EXISTS {?y ns:government.government_position_held.to ?sk2} || 
        EXISTS {?y ns:government.government_position_held.to ?sk3 . 
        FILTER(xsd:gYear(?sk3) >= \"1980\"^^xsd:gYear) })}
      """
  utils = QueryGraphUtils(use_tdb_query=True, kb_type="freebase", kb_index_path="/tuna1/indexes/d-freebase")
  parse, graph = utils.sparql_to_graph(sparql=sparql, is_grounding=True)
  return graph, utils


class TestQueryGraphUtils(object):

  def test_sparql_to_graph(self, setup):
    graph, utils = setup
    assert len(graph.get_edges()) == 4

  def test_query_graph_stage_generation(self, setup):
    graph, utils = setup
    query_graph_stages = utils.query_graph_stage_generation(
      sentence="Who was the president in 1980 of the country that has Azad Kashmir?",
      query_graph=graph)
    assert len(query_graph_stages) == 4
    for stage in query_graph_stages:
      stage_testing_examples = stage.to_testing_example(utils=utils)
      stage_training_examples = stage.to_training_example(utils=utils)
