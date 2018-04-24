"""
Get all props from wikidata and recreate them
with equiv prop links to wikidata
"""

from tqdm import tqdm
from wikidataintegrator import wdi_core, wdi_login
from init import create_property

from config import WDQS_FRONTEND, WIKIBASE_PORT, USER, PASS, HOST

mediawiki_api_url = "http://{}:{}/w/api.php".format(HOST, WIKIBASE_PORT)
sparql_endpoint_url = "http://{}:{}/proxy/wdqs/bigdata/namespace/wdq/sparql".format(HOST, WDQS_FRONTEND)
localItemEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)

login = wdi_login.WDLogin(USER, PASS, mediawiki_api_url=mediawiki_api_url)

datatype_map = {'http://wikiba.se/ontology#CommonsMedia': 'commonsMedia',
                'http://wikiba.se/ontology#ExternalId': 'external-id',
                'http://wikiba.se/ontology#GeoShape': 'geo-shape',
                'http://wikiba.se/ontology#GlobeCoordinate': 'globe-coordinate',
                'http://wikiba.se/ontology#Math': 'math',
                'http://wikiba.se/ontology#Monolingualtext': 'monolingualtext',
                'http://wikiba.se/ontology#Quantity': 'quantity',
                'http://wikiba.se/ontology#String': 'string',
                'http://wikiba.se/ontology#TabularData': 'tabular-data',
                'http://wikiba.se/ontology#Time': 'time',
                'http://wikiba.se/ontology#Url': 'url',
                'http://wikiba.se/ontology#WikibaseItem': 'wikibase-item',
                'http://wikiba.se/ontology#WikibaseProperty': 'wikibase-property'}


def get_prop_info_from_wikidata():
    props = get_wd_props()
    equiv = get_equiv_props()
    for k, v in props.items():
        props[k].update(equiv.get(k, dict()))
        equiv_props = ["http://www.wikidata.org/entity/" + v['p'].split("/")[-1]]
        equiv_props.extend(v["equivs"].split("|") if "equivs" in v else [])
        v['equivs'] = equiv_props
    props = {k.rsplit("/", 1)[-1]: v for k, v in props.items()}
    return props


def get_wd_props():
    # Get all props, inclusing labels, descriptions, aliases, from wikidata
    query = '''SELECT ?p ?pt ?pLabel ?d ?aliases WHERE {
      {
        SELECT ?p ?pt ?d (GROUP_CONCAT(DISTINCT ?alias; separator="|") as ?aliases) WHERE {
          ?p wikibase:propertyType ?pt .
          OPTIONAL {?p skos:altLabel ?alias FILTER (LANG (?alias) = "en")}
          OPTIONAL {?p schema:description ?d FILTER (LANG (?d) = "en") .}
        } GROUP BY ?p ?pt ?d
      }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }'''
    results = wdi_core.WDItemEngine.execute_sparql_query(query)
    results = results['results']['bindings']
    d = [{k: v['value'] for k, v in item.items()} for item in results]
    d = {x['p']: x for x in d}
    return d


def get_equiv_props():
    query = '''SELECT ?p (GROUP_CONCAT(DISTINCT ?equiv; separator="|") as ?equivs) WHERE {
      ?p wikibase:propertyType ?pt .
      ?p wdt:P1628 ?equiv
    } GROUP BY ?p'''
    results = wdi_core.WDItemEngine.execute_sparql_query(query)
    results = results['results']['bindings']
    d = [{k: v['value'] for k, v in item.items()} for item in results]
    d = {x['p']: x for x in d}
    return d


def create_property_from_pid(pid):
    prop = PROP_INFO[pid]
    return create_property(prop['pLabel'], prop['d'], datatype_map[prop['pt']], prop['equivs'], login)


PROP_INFO = get_prop_info_from_wikidata()

if __name__ == "__main__":
    for prop in tqdm(PROP_INFO.values()):
        try:
            create_property(prop['pLabel'], prop['d'], datatype_map[prop['pt']], prop['equivs'], login)
        except Exception as e:
            pass
