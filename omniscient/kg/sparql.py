from SPARQLWrapper import SPARQLWrapper2, JSON


class SPARQL:

  def __init__(self, name, endpoint, format=JSON):
    self.name = name
    self.endpoint = endpoint
    self.format = format
    self.sparql = SPARQLWrapper2(self.endpoint)
    self.sparql.setReturnFormat(format)

  def query(self, q):
    """Runs a query and returns all bindings"""
    self.sparql.setQuery(q)
    results = self.sparql.query().bindings
    return results

  def query_repeat(self, q, limit=10000, offset=0, max=None):
    """Runs a query and returns all bindings"""
    q += " limit {} offset {}"

    results = []

    while True:
      self.sparql.setQuery(q.format(limit, offset))
      bindings = self.sparql.query().bindings
      print("Returned", len(bindings), "Total", len(results))
      if len(bindings) == 0 or (max is not None and len(results) >= max):
        break
      results += bindings
      offset += len(bindings)
    return results

  def get_sparql_object(self):
    return self.sparql

  def get_all_types(self):
    """Retrieves all type URIs from the dataset"""
    results = self.query_repeat("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?type WHERE {{
                ?s rdf:type ?type
            }}
        """)
    types = []
    for result in results:
      types.append(result["type"].value)
    return types

  def get_all_properties(self):
    """Retrieves all property URIs from the dataset"""
    results = self.query_repeat("""
        SELECT DISTINCT ?p WHERE {{
                ?s ?p ?o
            }}
        """)
    properties = []
    for result in results:
      properties.append(result["p"].value)
    return properties

  def get_entities_with_type(self, entity_type):
    """Returns all entity URIs with type entity_type."""
    results = self.query_repeat("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?a WHERE {{
            ?a rdf:type <""" + entity_type + """>
          }}""")
    entities = []
    for result in results:
      entities.append(result["a"].value)
    print(len(entities))
    return entities

  def get_properties_for_entity(self, entity):
    """Given an entity, retrieves its properties and property values in
    two separate (matching) arrays"""
    results = self.query_repeat("""
        SELECT ?p ?o WHERE {{
            <""" + str(entity) + """> ?p ?o
        }}
        """)
    properties = []
    values = []
    for result in results:
      properties.append(result["p"].value)
      values.append(result["o"].value)
    return list(zip(properties, values))
