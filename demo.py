import time

import pandas as pd
from wikidataintegrator import wdi_core, wdi_login, wdi_helpers

from time import strftime, gmtime
from tqdm import tqdm
from init import get_quiv_prop_pid

from wikidataintegrator import wdi_property_store

from config import WDQS_FRONTEND, WIKIBASE_PORT, USER, PASS, HOST

mediawiki_api_url = "http://{}:{}/w/api.php".format(HOST, WIKIBASE_PORT)
sparql_endpoint_url = "http://{}:{}/proxy/wdqs/bigdata/namespace/wdq/sparql".format(HOST, WDQS_FRONTEND)
localItemEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)

login = wdi_login.WDLogin(USER, PASS, mediawiki_api_url=mediawiki_api_url)

uri_map = wdi_helpers.id_mapper(get_quiv_prop_pid(), endpoint=sparql_endpoint_url)
wdi_property_store.wd_properties[uri_map['http://identifiers.org/taxonomy/']] = {'core_id': True}
wdi_property_store.wd_properties[uri_map['http://www.wikidata.org/entity/P4333']] = {'core_id': True}


PROPS = {
    'NCBI Taxonomy ID': 'http://identifiers.org/taxonomy/',  # P685
    # 'NCBI Taxonomy ID': 'http://www.wikidata.org/entity/P685',
    'GenBank Assembly accession': 'http://www.wikidata.org/entity/P4333',
    'stated in': 'http://www.wikidata.org/entity/P248',
    'retrieved': 'http://www.wikidata.org/entity/P813',
    'reference URL': 'http://www.wikidata.org/entity/P854',
    'official website': 'http://www.wikidata.org/entity/P856'
}

ITEMS = {
    'GenBank': 'Q2' # change me
}

# load in csv
df = pd.read_csv("prokaryotes.txt", sep='\t', low_memory=False)
df.drop_duplicates("TaxID", keep=False, inplace=True)


def create_reference(genbank_id):
    stated_in = wdi_core.WDItemID(ITEMS['GenBank'], uri_map[PROPS['stated in']], is_reference=True)
    retrieved = wdi_core.WDTime(strftime("+%Y-%m-%dT00:00:00Z", gmtime()), uri_map[PROPS['retrieved']], is_reference=True)
    url = "https://www.ncbi.nlm.nih.gov/genome/?term={}".format(genbank_id)
    ref_url = wdi_core.WDUrl(url, uri_map[PROPS['reference URL']], is_reference=True)
    return [stated_in, retrieved, ref_url]


def run_one(row):
    label = row['#Organism/Name']
    taxid = str(row['TaxID'])
    genbank_id = row['Assembly Accession']
    s = [
        wdi_core.WDExternalID(genbank_id, uri_map[PROPS['GenBank Assembly accession']], references=[create_reference(genbank_id)]),
        wdi_core.WDExternalID(taxid, uri_map[PROPS['NCBI Taxonomy ID']], references=[create_reference(genbank_id)]),
    ]
    item = localItemEngine(data=s, item_name=label, domain="organism",
                           fast_run=True, fast_run_base_filter={uri_map[PROPS['NCBI Taxonomy ID']]:''})
    item.set_label(label)
    item.set_description("bug")
    wdi_helpers.try_write(item, login=login, record_id=genbank_id, record_prop=uri_map[PROPS['GenBank Assembly accession']])


for _,row in tqdm(df.iterrows(), total=len(df)):
    run_one(row)