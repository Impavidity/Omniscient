from flask import Flask, jsonify, request
from flask_cors import CORS
from omniscient.linking.simple_linker import EntityLinker

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

linker = EntityLinker({
    "freebase": "/tuna1/indexes/s-freebase",
    "dbpedia": "/tuna1/indexes/s-dbpedia",
    "wikidata": "/tuna1/indexes/s-wikidata"})

@app.route('/')
def index():
  return jsonify("Hello world!")

@app.route('/api/linking', methods=['GET'])
def search():
  mention = request.args['mention']
  candidates = linker.link(mention=mention)
  return jsonify(candidates)


app.run(host="0.0.0.0", port=5001, debug=True)
