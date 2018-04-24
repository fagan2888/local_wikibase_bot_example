"""
On a fresh wikibase, run init.sh first


"""

import time
from wikidataintegrator import wdi_core, wdi_login, wdi_helpers

from init import get_quiv_prop_pid
from make_props import create_property_from_pid

from config import WDQS_FRONTEND, WIKIBASE_PORT, USER, PASS, HOST

mediawiki_api_url = "http://{}:{}/w/api.php".format(HOST, WIKIBASE_PORT)
sparql_endpoint_url = "http://{}:{}/proxy/wdqs/bigdata/namespace/wdq/sparql".format(HOST, WDQS_FRONTEND)
localItemEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)

print("login")
login = wdi_login.WDLogin(USER, PASS, mediawiki_api_url=mediawiki_api_url)

PROPS = {
    'NCBI Taxonomy ID': 'P685',
    'GenBank Assembly accession': 'P4333',
    'stated in': 'P248',
    'retrieved': 'P813',
    'reference URL': 'P854',
    'official website': 'P856'
}

# create properties I need
for prop in PROPS.values():
    p = create_property_from_pid(prop)
    print("created property {}: {}".format(p.wd_item_id, prop))

time.sleep(10)

uri_map = wdi_helpers.id_mapper(get_quiv_prop_pid(), endpoint=sparql_endpoint_url)

# create items I need
item = localItemEngine(data=[wdi_core.WDString("http://www.ncbi.nlm.nih.gov/genbank/",
                                               uri_map['http://xmlns.com/foaf/0.1/homepage'])], domain='x', item_name="GenBank")
item.set_label("GenBank")
item.set_description('DNA sequence database')
item.write(login)

ITEMS = {
    'GenBank': item.wd_item_id
}
