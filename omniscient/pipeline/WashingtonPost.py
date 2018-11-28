# WashingtonPost has 595037 documents in total
import click
import json
from bs4 import BeautifulSoup
from multiprocessing import Pool, Value, Lock
import datetime
import math


class AtomicCounter(object):
  def __init__(self):
    self.value = Value("i", 0)
    self.lock = Lock()

  def increment(self):
    with self.lock:
      self.value.value += 1
      return self.value.value
counter = AtomicCounter()


class SpacyMagic(object):
  """
  Simple Spacy Magic to minimize loading time.
  >>> SpacyMagic.get("en")
  <spacy.en.English ...
  """
  _spacys = {}

  @classmethod
  def get(cls, lang):
    if lang not in cls._spacys:
      import spacy
      cls._spacys[lang] = spacy.load(lang, disable=['tagger', 'parser'])
    return cls._spacys[lang]

class StanfordCoreNLPMagic(object):
  _corenlp = None

  @classmethod
  def get(cls, lang):
    if cls._corenlp is None:
      from omniscient.pipeline.StanfordNLP import StanfordNLP
      cls._corenlp = StanfordNLP()
    return cls._corenlp


@click.group()
def cli():
  pass

def extract(line):
  model = SpacyMagic.get("en")
  corenlp = StanfordCoreNLPMagic.get("en")
  example = json.loads(line)
  id = example['id']
  title = example['title']
  article_url = example['article_url']
  doc = None
  if title:
    try:
      html = " ".join(filter(lambda x: x is not None,
              [paragraph['content']
               if ('content' in paragraph and paragraph['type'] == 'sanitized_html')
               else None for paragraph in example['contents']]))
      if len(html) > 0:
        soup = BeautifulSoup(html, "html5lib")
        sentences = soup.get_text()
        doc = []
        sentences = corenlp.sent_tokenize(sentences)
        for sentence in sentences:
          parsed = model(sentence)
          entities = []
          for ent in parsed.ents:
            entities.append({
              "text": ent.text,
              "start_char": ent.start_char,
              "end_char": ent.end_char,
              "label": ent.label_
            })
          tokenized_sentences = " ".join([token.text for token in parsed])
          doc.append({
            "sentence": tokenized_sentences,
            "entities": entities})
    except:
      click.echo("{} is broken".format(id))
      doc = None
  count = counter.increment()
  if count % 10000 == 0:
    click.echo("[{}] {} documents processed.".format(datetime.datetime.now(), count))

  return json.dumps({
    "id": id,
    "title": title,
    "article_url": article_url,
    "content": doc})

@click.command()
@click.option("--file_path", type=str, required=True)
@click.option("--output_path", type=str, required=True)
@click.option("--partition_num", type=int, required=True)
@click.option("--start_from", type=int, required=True)
def process(file_path, output_path, partition_num, start_from):
  pool = Pool(60)
  click.echo("[{}] Create Pool".format(datetime.datetime.now()))
  click.echo("[{}] Start loading file".format(datetime.datetime.now()))
  lines = open(file_path).readlines()
  total_size = len(lines)
  partition_size = math.ceil(total_size / partition_num)
  partitions = [lines[partition_size * i : partition_size * (i + 1)] for i in range(partition_num)]
  del lines
  click.echo("[{}] Finish file loading".format(datetime.datetime.now()))
  for idx, partition in enumerate(partitions):
    if idx < start_from:
      continue
    click.echo("[{}] Start extraction on part {}".format(datetime.datetime.now(), idx))
    results = pool.map(extract, partition)
    click.echo("[{}] Finish extraction on part {}".format(datetime.datetime.now(), idx))
    with open(output_path + "-{}".format(idx), "w") as fout:
      for example in results:
        fout.write(example + "\n")
    click.echo("[{}] Finish dumping for part {}".format(datetime.datetime.now(), idx))
  click.echo("[{}] Finish Extraction for all partition".format(datetime.datetime.now()))
cli.add_command(process)

if __name__ == "__main__":
  cli()