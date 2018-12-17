# -*- coding: utf-8 -*-
import re
from enum import Enum


DBPEDIA_FOAF_LONG = "http://xmlns.com/foaf/0.1/name"
LANG_EN = "en"
LANG_ZH = "zh"

RDF_OBJECT_TYPE = Enum('RDF_OBJECT_TYPE', ('URI', 'STRING', 'TEXT', 'OTHER'))
FOO = "<foo>"

class DBpediaNode(object):
  def __init__(self, uri):
    self.uri = uri
    self.predicate_values = {}

  def add_predicate_value(self, p, o):
    if p not in self.predicate_values:
      self.predicate_values[p] = []
    self.predicate_values[p].append(o)

  def __str__(self):
    string_builder = []
    for predicate in self.predicate_values:
      for value in self.predicate_values[predicate]:
        string_builder.extend([self.uri, "\t", predicate, "\t", value, "\t.\n"])
    return "".join(string_builder)

  @staticmethod
  def clean_uri(uri):
    if uri[0] == '<':
      uri = uri[1: -1]
    return uri.strip()

  @staticmethod
  def get_object_type(value):
    if value[0] == "<":
      # e.g., <http://rdf.freebase.com/ns/m.02mjmr>
      return RDF_OBJECT_TYPE.URI
    if value[0] == '"':
      if value[-1] == '"':
        # e.g., "Hanna Bieluszko"
        return RDF_OBJECT_TYPE.STRING
      else:
        # e.g., "Hanna Bieluszko"@en;
        return RDF_OBJECT_TYPE.TEXT
    return RDF_OBJECT_TYPE.OTHER

  @staticmethod
  def undo_mql_key_escape(value):
    pass

  @staticmethod
  def remove_enclosing_quote(value):
    if value[0] == '"':
      return value[1:-1]
    return value

  @staticmethod
  def unquotekey(key, encoding=None):
    """
    unquote a namespace key and turn it into a unicode string
    """
    part = key.split("$")
    output = [part[0]]
    for i in range(1, len(part)):
      try:
        output.append(chr(int(part[i][0:4], 16)))
        output.append(part[i][4:])
      except:
        output.append(part[i])

    ustr = ''.join(output)

    if encoding is None:
      return ustr

    return ustr.encode(encoding)

  @staticmethod
  def normalize_object_value(value, language_filter=list([LANG_EN])):
    value_type = DBpediaNode.get_object_type(value)
    if value_type == RDF_OBJECT_TYPE.URI:
      return DBpediaNode.clean_uri(value)
    elif value_type == RDF_OBJECT_TYPE.STRING:
      # If the object is a string, remove enclosing quote.
      if "$" in value:
        # // See comment below about MQL key escaping
        return DBpediaNode.unquotekey(DBpediaNode.remove_enclosing_quote(value))
      else:
        return DBpediaNode.remove_enclosing_quote(value)
    elif value_type == RDF_OBJECT_TYPE.TEXT:
      label, language, datatype = DBpediaNode.parse_literal(value)
      if language is not None:
        if language in language_filter:
          return label
        else:
          return ""
      return label
    else:
      return value

  @staticmethod
  def unescape_string(label):
    # Only works for python3
    return label.encode('utf-8').decode('unicode_escape')

  @staticmethod
  def unescape(text):
    regex = re.compile(b'\\\\(\\\\|[0-7]{1,3}|x.[0-9a-f]?|[\'"abfnrt]|.|$)')

    def replace(m):
      b = m.group(1)
      if len(b) == 0:
        raise ValueError("Invalid character escape: '\\'.")
      i = b[0]
      if i == 120:
        v = int(b[1:], 16)
      elif 48 <= i <= 55:
        v = int(b, 8)
      elif i == 34:
        return b'"'
      elif i == 39:
        return b"'"
      elif i == 92:
        return b'\\'
      elif i == 97:
        return b'\a'
      elif i == 98:
        return b'\b'
      elif i == 102:
        return b'\f'
      elif i == 110:
        return b'\n'
      elif i == 114:
        return b'\r'
      elif i == 116:
        return b'\t'
      else:
        s = b.decode('ascii')
        raise UnicodeDecodeError(
          'stringescape', text, m.start(), m.end(), "Invalid escape: %r" % s
        )
      return bytes((v,))

    result = regex.sub(replace, text.encode('utf-8'))
    return result.decode("utf-8")

  @staticmethod
  def parse_literal(value):
    if value.startswith("\""):
      # Find string separation points
      end_label_idx = DBpediaNode.find_end_of_label(value)
      if end_label_idx != -1:
        try:
          start_lang_idx = value[end_label_idx:].index("@") + end_label_idx
        except ValueError:
          start_lang_idx = -1
        try:
          start_dt_idx = value[end_label_idx:].index("^^") + end_label_idx
        except ValueError:
          start_dt_idx = -1
        if start_lang_idx != -1 and start_dt_idx != -1:
          raise ValueError("Literals {} can not have both a language and a datatype".format(value))
        label = value[1:end_label_idx]
        label = DBpediaNode.unescape(label)
        # print(label)
        # print(type(label), label)
        if start_lang_idx != -1:
          language = value[start_lang_idx+1:]
          return label, language, None
        elif start_dt_idx != -1:
          datatype = value[start_dt_idx+2:]
          return label, None, datatype
        else:
          return label, None, None
    raise ValueError("Not a legal N-Triples literal: {}".format(value))

  @staticmethod
  def find_end_of_label(value):
    previous_was_backslash = False
    for i in range(1, len(value)):
      c = value[i]
      if c == '"' and not previous_was_backslash:
        return i
      elif c == '\\' and not previous_was_backslash:
        # start of escape
        previous_was_backslash = True
      elif previous_was_backslash:
        # c was escaped
        previous_was_backslash = False
    return -1

if __name__ == "__main__":
  l1 = "\"1954-10-28\"^^<http://www.w3.org/2001/XMLSchema#date>"
  l2 = "\"Hanna Bieluszko\"@en"
  assert(DBpediaNode.parse_literal(l1)[0] == "1954-10-28")
  assert(DBpediaNode.parse_literal(l2)[0] == "Hanna Bieluszko")
  assert(DBpediaNode.get_object_type("<http://dbpedia.org/resource/Michael_Jackson>") == RDF_OBJECT_TYPE.URI)
  assert(DBpediaNode.get_object_type("\"1954-10-28\"^^<http://www.w3.org/2001/XMLSchema#date>") == RDF_OBJECT_TYPE.TEXT)
  assert(DBpediaNode.get_object_type("\"Hanna Bieluszko\"@en") == RDF_OBJECT_TYPE.TEXT)
  assert(DBpediaNode.get_object_type("\"Hanna Bieluszko\"") == RDF_OBJECT_TYPE.STRING)
  assert(DBpediaNode.unescape_string("This is a multi-line\nliteral with many quotes (\"\"\"\"\")\nand two apostrophes ('').") ==
         "This is a multi-line\nliteral with many quotes (\"\"\"\"\")\nand two apostrophes ('').")
  assert(DBpediaNode.parse_literal("\" \\t \\b \\n \\r \\f \\\" \\' \\\\ \"")[0] == " \t \b \n \r \f \" \' \\ ")
  # print(FreebaseNode.unquotekey("Barack_Hussein_Obama$002C_Jr$002E"))
  assert(DBpediaNode.unquotekey("Barack_Hussein_Obama$002C_Jr$002E") == "Barack_Hussein_Obama,_Jr.")
  # print(u"\"José \\nLópez-Rey\"@en")
  # print(FreebaseNode.unescape("\"José \\nLópez-Rey\"@en"))
  # print((FreebaseNode.normalize_object_value("\"José \\nLópez-Rey\"@en")))