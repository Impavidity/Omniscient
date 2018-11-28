from jnius import autoclass

class StanfordNLP(object):
  def __init__(self):
    self.JString = autoclass('java.lang.String')
    self.JArray = autoclass("java.lang.reflect.Array")
    self.Document = autoclass("edu/stanford/nlp/simple/Document")

  def sent_tokenize(self, doc):
    doc = self.Document(self.JString(doc.encode("utf-8")))
    sentences = doc.sentences()
    sentences_list = []
    for i in range(sentences.size()):
      sentences_list.append(sentences.get(i).toString())
    return sentences_list

if __name__ == "__main__":
  tool = StanfordNLP()
  tool.sent_tokenize("""At 7:10 a.m. Friday, Mr. Powers, a 50-year-old mortgage banker in tapered-temple glasses, arrived for the Romney rally outside a local supermarket in a red golf sweatshirt. His wife, who also thought the event would be held indoors, arrived soon after in a yellow sweater, black vest and paisley-printed slacks.""")