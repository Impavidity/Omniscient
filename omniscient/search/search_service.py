from flask import Flask, jsonify, request
from flask_cors import CORS
from omniscient.search.simple_search import SimpleSearcher

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
PATH = "/data/wyang/UnstructQA/index/lucene-index.wiki20190301_paragraph.pos+docvectors"
searcher = SimpleSearcher(path=PATH)

@app.route('/')
def index():
  return jsonify("Hello world!")

@app.route('/api/search', methods=['GET'])
def search():
  query = request.args['query']
  candidates = searcher.query(qstring=query)
  return jsonify(candidates)


app.run(host="0.0.0.0", port=5000, debug=True)

