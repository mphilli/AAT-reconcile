from lxml import etree
import requests
import difflib
from SPARQLWrapper import SPARQLWrapper, JSON


BASE_URI = "http://vocabsservices.getty.edu/AATService.asmx/AATGetTermMatch?term="
END_URI = "&logop=and&notes="


class Recon:

    def __init__(self, score):
        """Turns the lists of scores and term-id pairs into objects"""
        self.score = score[0]
        self.term = score[1][0]
        self.id = score[1][1]
        self.uri = get_term_uri(self.id)

    def __str__(self):
        return str(self.term) + " (" + str(self.score) + ")"


class SPARQLQuery:

    def __init__(self, search_term):
        """Perform AAT genre searches by querying the controlled vocabulary's SPARQL endpoint"""
        self.term = search_term
        self.results = self.query_sparql_endpoint()

    def __repr__(self):
        return self.results

    def query_sparql_endpoint(self):
        sparql = SPARQLWrapper("http://vocab.getty.edu/sparql")
        sparql.setQuery("""
            SELECT ?Subject ?Term  WHERE {
            ?Subject a skos:Concept; luc:term \"""" + self.term + """\"; skos:inScheme aat: ;
            gvp:prefLabelGVP [xl:literalForm ?Term].
            } ORDER BY asc(lcase(str(?Term)))
            """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        if results:
            term_id_pairs = [(r["Term"]["value"], r["Subject"]["value"])
                             for r in results["results"]["bindings"]]
            return term_id_pairs
        return None


def search_thesaurus(term):
    """searches for the term using the API (returns XML)"""
    # start = time.time()  # for testing
    response = requests.get(BASE_URI + term.replace(" ", "+") + END_URI, stream=True)
    response.raw.decode_content = True
    lxml = etree.parse(response.raw)
    term_results = lxml.getroot().xpath("/Vocabulary/Subject")
    pref_tuples = []
    for i in range(0, len(term_results)):
        pref_term = lxml.getroot().xpath("/Vocabulary/Subject/Preferred_Term")[i].text
        pref_parent = lxml.getroot().xpath("/Vocabulary/Subject/Subject_ID")[i].text
        pref_tuples.append((pref_term, pref_parent))
    # print("search thesaurus took " + str(time.time() - start) + " for " + str(subject))
    return pref_tuples


def get_term_uri(term_id, extension="html", include_ext=False):
    """:return: the URI of a term, given the retrieved ID"""
    if "http://" in term_id:
        return term_id
    term_uri = "http://vocab.getty.edu/aat/" + term_id
    if include_ext:
        return term_uri + "." + extension
    return term_uri


def reconcile(search_term, term_id_pairs, sort=False, limit=5):
    """appends a reconciliation score to each aat_term-identifier pair"""
    recon_scores = []
    for t in term_id_pairs:
        # NOTE: assumes 0th element of tuple == aat_term
        aat_term = t[0].lower()
        if aat_term.endswith("."):
            aat_term = aat_term[-1]
        sim_ratio = str(round(float(difflib.SequenceMatcher(
            None,
            search_term.lower(),
            aat_term).ratio()), 3))
        recon_scores.append([sim_ratio, t])
    if sort:
        return sorted(recon_scores,
                      key=lambda x: x[0],
                      reverse=True)[:limit]
    return recon_scores[:limit]
