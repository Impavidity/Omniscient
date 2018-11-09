# Omniscient
Knowledge Extraction, Graph Construction and exciting Applications


## Requirement

- Spacy
```code
conda config --add channels conda-forge
conda install spacy
python -m spacy download en
```

## Build Inverted Index for Freebase

- Download the freebase dump from [here](https://developers.google.com/freebase/)
- Extract names from dumps
```code
nohup python -u -m kg.freebase.name_extraction --input /path/to/freebase/freebase-rdf-latest.gz --output_path /path/to/index/ --output_file freebase_name.json > freebase_name_extraction.log &
```
The total node size is 125144313, it roughly takes 12.5 h to build the index
- Build Index from the json file
```code
nohup python -u -m kg.freebase.inverted_index --input /path/to/freebase_name.json --index /path/to/index/path > inverted_index_freebase_db.log &
```
- Search
```code
python -m kg.freebase.candidate_retrieval --index /path/to/index/path  --query obama
```