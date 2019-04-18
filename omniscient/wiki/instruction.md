# Preprocess the wikipedia dump

## Download the wikipedia dump

We need the page article dump `{language}wiki-{yyyymmdd}-pages-articles.xml.bz2`. 

## Parsing

We use the `WikiExtractor` [here](https://github.com/attardi/wikiextractor) to parse the dump.

Use Germany as an example, the following command is used to parse the dump.
```commandline
nohup python WikiExtractor.py --json -l -b 2000M -o /path/to/collections/wiki/extraction/de /path/to/collections/wiki/dewiki-20181201-pages-articles.xml.bz2  > extraction_de.log &
``` 

## Cleaning

1. Load extracted data.
