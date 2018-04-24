wikibase-docker little wiki setup

https://github.com/wmde/wikibase-docker

https://github.com/wmde/wikibase-docker/blob/master/README-compose.md


----

```
virtualenv -p python3 venv
source venv/bin/activate
pip install wikidataintegrator pandas tqdm jupyter
```

1. set params in config.py

2. Run `setup_wikibase.sh`

3. Run `python3 init.py`

4. Run `python3 demo_setup.py`

5. `wget -nc ftp://ftp.ncbi.nlm.nih.gov/genomes/GENOME_REPORTS/prokaryotes.txt`

6. Run `python3 demo.py`