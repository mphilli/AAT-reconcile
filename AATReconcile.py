# A simple reconciliation service for reconciling terms from the Art & Architecture Thesaurus (AAT) for OpenRefine
# You can choose to search from the thesauraus using their API or their SPARQL endpoint
# 3/13/2018 - Michael G Phillips


from flask import Flask, request, jsonify, json
import reconciliation as recon
from reconciliation import SPARQLQuery

app = Flask(__name__)

metadata = {
    "name": "AAT Reconciliation Service",
    "defaultTypes": [{"id": "/vocabularies/aat",
                      "name": "Thesaurus Terms"}],
    "view": {
            "url": "{{id}}"
        }
}


def preprocess(token):

    tokens = token.split(" ")
    for i, t in enumerate(tokens):
        if ")" in t or "(" in t:
            tokens[i] = ''
    token = " ".join(tokens)
    if token.endswith("."):
        token = token[:-1]
    return token.lower().lstrip().rstrip()


def search(search_in, limit=3, sparql=False):
    scores = []
    search_token = preprocess(search_in)
    if sparql:
        query_result = SPARQLQuery(search_term=search_token).results
    else:
        query_result = recon.search_thesaurus(subject=search_token)

    if search_in.endswith("."):
        search_in = search_in[:-1]
    # print(search_in, search_token)
    recon_ = recon.reconcile(search_in, query_result, sort=True, limit=limit)
    for r in recon_:
        match = False
        recon_result = recon.Recon(r)
        # logging.info("Recon object: " + str(recon_result))
        if recon_result.score == "1.0":
            match = True
        scores.append({
            "id": str(recon_result.uri),
            "name": recon_result.term,
            "score": recon_result.score,
            "match": match,
            "type": metadata['defaultTypes'],
        })
    return scores


def jsonpify(obj):
    try:
        callback = request.args['callback']
        response = app.make_response("%s(%s)" % (callback, json.dumps(obj)))
        response.mimetype = "text/javascript"
        return response
    except KeyError:
        return jsonify(obj)


@app.route("/reconcile/AAT", methods=['POST', 'GET'])
def reconcile():
    queries = request.form.get('queries')
    if queries:
        queries = json.loads(queries)
        results = {}
        for (key, query) in queries.items():
            qtype = query.get('type')
            if qtype is None:
                return jsonpify(metadata)
            limit = 3
            if 'limit' in query:
                limit = int(query['limit'])
            # performance testing reveals that querying the SPARQL endpoint is superior
            results[key] = {"result": search(query['query'],
                                             limit=limit,
                                             sparql=True
                                             )}
        return jsonpify(results)
    return jsonpify(metadata)


@app.route("/")
def render_index():
    """return text message to localhost:5000"""
    return "AAT Reconciliation Service is running on this port!"


if __name__ == "__main__":
    app.run(debug=False)
