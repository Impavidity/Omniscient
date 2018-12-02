import copy
import json
import os
import uuid
import subprocess

from omniscient.structure.query_graph import QueryGraph
from omniscient.structure.stage import Stage
from omniscient.structure.sentence import Sentence
from omniscient.structure.mention import Mention
from omniscient.structure import constant
try:
  from omniscient.kg.tdb_query import TDBQuery
except:
  pass


TMP_DIR = "sparql_tmp"

class QueryGraphUtils(object):

  def __init__(
        self,
        use_tdb_query=False,
        kb_type=None,
        kb_index_path=None):
    self.use_tdb_query = use_tdb_query
    self.kb_type = kb_type
    self.kb_index_path = kb_index_path
    self.query_client = None
    if use_tdb_query and kb_type and kb_index_path:
      self.query_client = TDBQuery(path=self.kb_index_path)

  def sparql_to_json(self, sparql):
    """
    Args:
      sparql:
    Returns:
    """
    if not os.path.exists(TMP_DIR):
      os.mkdir(TMP_DIR)
    tmp_file_path = os.path.join(TMP_DIR, str(uuid.uuid4()))
    with open(tmp_file_path, "w") as query_fout:
      refined_sparql = "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n{}\n".format(
        sparql.strip().replace(" OR ", " || "))
      query_fout.write(refined_sparql)
    json_string = subprocess.check_output(
      'sparql-to-json {}'.format(tmp_file_path), shell=True).decode("utf-8")
    json_dict = json.loads(json_string)
    os.remove(tmp_file_path)
    return json_dict, refined_sparql

  def json_to_graph(self, json_dict, sparql=None):
    """
    This function is to convert the json dict into
      `QueryGraph`
    Args:
      json_dict (dict): the output of sparql2json
    Returns: QueryGraph
    """
    query_graph = QueryGraph(sparql)
    for where_args in json_dict["where"]:
      if where_args["type"] == "bgp":
        for triple in where_args["triples"]:
          query_graph.add_edge((triple["subject"], triple["predicate"], triple["object"]))
    return query_graph

  def sparql_to_graph(self, sparql, is_grounding=False, grounded_results=None):
    """
    This function is to convert full sparql query into
      `QueryGraph`
    Args:
      sparql (str): sparql query

    Returns: Tuple(json_dict, `QueryGraph`)
    """
    sparql_parse_json, refined_sparql = self.sparql_to_json(sparql=sparql)
    graph = self.json_to_graph(json_dict=sparql_parse_json, sparql=refined_sparql)
    if is_grounding:
      if grounded_results:
        graph.grounding(grounded_results=grounded_results)
      elif self.query_client:
        results = self.query_client.query(refined_sparql.replace(
          "DISTINCT ?x", "DISTINCT *").encode("utf-8"))
        graph.grounding(grounded_results=results)
      else:
        raise ValueError("Grounded results are needed or the query client should be initialized")
    return sparql_parse_json, graph

  def batch_grounding(self, graphs):
    """

    Args:
      graphs: Batching all graphs for parallel grounding

    Returns:

    """
    raise NotImplementedError

  def apply_action(self, query_graph, action):
    """
    Apply the action on a graph.
      We use the value of standpoint(Vertex), predicate(Edge) and target(Vertex) build
      the query graph step by step.
      We will not reuse the Vertex and Edge object because the `id` might be different
      from the original graph
    Args:
      query_graph (:obj:QueryGraph): Partial query graph
      action (:obj:Action): The action would be applied to the query graph
    Returns: QueryGraph
    """
    query_graph_new = copy.deepcopy(query_graph)
    if action.p_direction == constant.P_FORWARD:
      query_graph_new.add_edge((
        action.standpoint.value,
        action.predicate.value,
        action.target.value))
    elif action.p_direction == constant.P_BACKWARD:
      query_graph_new.add_edge((
        action.target.value,
        action.predicate.value,
        action.standpoint.value))
    return query_graph_new

  def query_graph_stage_generation(self, sentence, query_graph):
    """
    This function is to convert the `query_graph` (using the actions)
      into list of `stages`.
    Args:
      sentence (str)
      query_graph (QueryGraph)
    Returns: List[Stage]
    """
    actions = query_graph.graph_to_actions()
    query_graph = QueryGraph()
    stages = []
    variable_pool = []
    sent = Sentence(sentence)
    for action in actions:
      if action.standpoint.type == constant.URI:
        mention = Mention(linked_uri=action.standpoint.value)
      else:
        mention = None
      query_graph_new = self.apply_action(query_graph, action)
      stage = Stage(
        sentence=sent,
        query_graph=query_graph_new,
        standpoint=action.standpoint,
        variable_pool=copy.deepcopy(variable_pool),
        mention=mention,
        gold_predicate=action.predicate,
        action=action)
      stages.append(stage)
      if action == constant.GEN_VAR:
        variable_pool.append(len(variable_pool))
        """Update the variable pool"""
      query_graph = query_graph_new
    return stages

  def retrieve_neighbourhood_with_batch_graph(self, graphs, output_path):
    """
    Because of the problem of parallel TDBQuery, this will stage
      all the results in memory.
    Args:
      graphs:
      output_path:

    Returns:

    """
    raise NotImplementedError

  def retrieve_forward_neighbourhood_with_entity(self, entity):
    forward_result = self.query_client.query(
      constant.FORWARD_QUERY_TEMPLATE.format("<{}>".format(entity)).encode("utf-8"))
    return forward_result

  def retrieve_backward_neighbourhood_with_entity(self, entity):
    backward_result = self.query_client.query(
      constant.BACKWARD_QUERY_TEMPLATE.format("<{}>".format(entity)).encode("utf-8"))
    return backward_result

  def retrieve_neighbourhood_with_entity_list(self, entity_list, output_path=None, num_threads=30):
    batch_forward_queries = []
    batch_backward_queries = []
    for entity in entity_list:
      batch_forward_queries.append(
        constant.FORWARD_QUERY_TEMPLATE.format("<{}>".format(entity)).encode("utf-8"))
      batch_backward_queries.append(
        constant.BACKWARD_QUERY_TEMPLATE.format("<{}>".format(entity)).encode("utf-8"))
    if self.query_client:
      forward_results = self.query_client.parallel_query(batch_forward_queries, num_threads=num_threads)
      backward_results = self.query_client.parallel_query(batch_backward_queries, num_threads=num_threads)
    else:
      raise ValueError("The query client is not initialized")
    if output_path:
      with open(output_path, "w") as fout:
        for entity, forward_result, backward_result in zip(entity_list, forward_results, backward_results):
          fout.write(json.dumps({
            entity: {
            "forward_result": forward_result,
            "backward_result": backward_result }}) + "\n")
    else:
      return forward_results, backward_results

  def is_valid_predicate(self, predicate):
    if (predicate.startswith("http://rdf.freebase.com/ns/common") or
      predicate.startswith("http://rdf.freebase.com/ns/type") or
      predicate.startswith("http://rdf.freebase.com/key")):
      return False

    return True



if __name__ == "__main__":
  utils = QueryGraphUtils()
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
  query_graph_stages = utils.query_graph_stage_generation(
    sentence="Who was the president in 1980 of the country that has Azad Kashmir?",
    query_graph=query_graph)
  pair = False
  for stage in query_graph_stages:
    if pair:
      stage_examples = stage.to_training_example()
    else:
      stage_examples = stage.to_testing_example()
    print(stage_examples)