# Omniscient
Knowledge Extraction, Graph Construction and exciting Applications


## Requirement
- Package Install
```
git clone https://github.com/Impavidity/Omniscient.git
cd Omniscient
python setup.py install
```

- Spacy
```code
conda config --add channels conda-forge
conda install spacy
python -m spacy download en
```

- pyjnius

You may fail in installing the package because of `pyjnius`.
You might need to setup some config for conda lib

If you have this error,
```
anaconda3/compiler_compat/ld: cannot find -lpthread
anaconda3/compiler_compat/ld: cannot find -lc
```
try to `cd anaconda3/lib` and do
```
ln -s /lib/x86_64-linux-gnu/libpthread.so.0 libpthread.so
ln -s /lib/x86_64-linux-gnu/libc.so.6 libc.so 
```

- Dependencies
```
mkdir resource
cd resource
wget https://git.uwaterloo.ca/p8shi/jar/raw/master/tdbquery.jar
```

## Build Inverted Index for Freebase

- Download the freebase dump from [here](https://developers.google.com/freebase/)
- Extract names from dumps
```code
nohup python -u -m kg.freebase.name_extraction --input /path/to/freebase/freebase-rdf-latest.gz --output_path /path/to/index/ --output_file freebase_name.json > freebase_name_extraction.log &
```
- Build Index from the json file
```code
nohup python -u -m kg.freebase.inverted_index --input /path/to/freebase_name.json --index /path/to/index/path > inverted_index_freebase_db.log &
```
- Search
```code
python -m kg.freebase.candidate_retrieval --index /path/to/index/path  --query obama
```

## Query with TDB dataset

With freebase dump, you can use `jena` to build index to support `SPARQL` query. 
Here, we use `TDBLoader2`
```
apache-jena-3.6.0/bin/tdbloader2 --loc path_to_index/d-freebase path_to_freebase_dump
```
`--loc` specifies the path of index.
Then you can run 
```
python -m omniscient.kg.tdb_query --index path_to_index/d-freebase
```
for query.
There are two type of query `query`(single query) and `parallel_query`(batch query with specific thread number).
For more example, you can refer to `kg/tdb_query.py`.




