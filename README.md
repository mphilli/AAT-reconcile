## AATReconcile

The following is a Python (3) program that works with the 
OpenRefine [Reconciliation Service API](https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API) in order to reconcile terms from the [Art and Architecture Thesaurus Online](http://www.getty.edu/research/tools/vocabularies/aat/),
by querying the Getty Vocabularies [SPARQL endpoint](http://vocab.getty.edu/sparql) (or through their [Web Services API](http://www.getty.edu/research/tools/vocabularies/vocab_web_services.pdf)). 

Installation:

With Python installed, first install the program requirements with pip:
 
    python -m pip install -r requirements.txt
    
Then, run the `AATreconcile.py` file, which will start the service at `http://127.0.0.1:5000/reconcile/AAT`.


Usage: 

In OpenRefine, click the arrow of the column(s) containing the terms you wish to reconcile, and navigate to:
Reconcile > Start reconciling...

The reconcile menu should appear, at which point you should click on the "Add Standard Service" button in the bottom left.
Provide the URL of the service, which by default is `http://127.0.0.1:5000/reconcile/AAT`

The *AAT Reconciliation Service* should now appear in your reconciliation menu. Click on 'Start Reconciling', and the service should begin.

The results returned by the service should be the best matching terms, along with their URIs from Getty Vocabularies. 

Example: [bank statements](http://vocab.getty.edu/aat/300027476)
