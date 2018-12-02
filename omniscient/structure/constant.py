
FB_FULL = "http://rdf.freebase.com/ns/"
FB_SHORT = "ns:"
XSD_FULL = "http://www.w3.org/2001/XMLSchema#"
XSD_SHORT = "xsd:"

P_FORWARD = "forward"
P_BACKWARD = "backward"

GEN_VAR = "gen_var"
COPY_VAR = "copy_var"
ADD_VALUE = "add_value"

VARIABLE = "variable"
URI = "uri"
LITERAL = "literal"

NONE = "<NONE>"

FORWARD_QUERY_TEMPLATE = """
SELECT DISTINCT ?p
WHERE {{
    {0} ?p ?o .
}}
"""
BACKWARD_QUERY_TEMPLATE = """
SELECT DISTINCT ?p
WHERE {{
    ?s ?p {0} .
}}
"""