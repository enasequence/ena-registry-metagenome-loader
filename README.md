# ena-registry-metagenome-loader

ena-registry-metagenome-loader contains example dataset loading scripts for the ENA [Metagenome Exchange Registry](https://www.ebi.ac.uk/ena/registry/metagenome/api/).

Currently this contains the script **bulkLoadDatsets.py** that can be used to pull down INSDC ID-source ID mappings in bulk
from a provided url and load these as datasets into the [Metagenome Exchange Registry](https://www.ebi.ac.uk/ena/registry/metagenome/api/).

This script can be used by metagenome analysis resources who are registered as a **broker** for the MGX Registry. This can assist 
with initial or recurring loading to the registry.

If you are part of a long-term stable metagenomics analysis resource and are
interested in becoming a **broker** for the MGX Registry, please [contact us](https://www.ebi.ac.uk/ena/browser/support) 
at the ENA to see if you are eligible. 

## Installation

The script uses Python and the [pandas](https://pandas.pydata.org/) library.

You can use the package manager [pip](https://pip.pypa.io/en/stable/) to install pandas.

```
pip install pandas
```

## Setting up the config.py file

To load datasets specific to your resource, you will need to tailor the config to your use-case. This 
config file has three sections:

#### Information about the broker 

This section requests information about the analysis resource and broker set up:

- BROKER_ID - this is provided when a resource registers to be a broker to the MGX registry
- AUTHORISATION_TOKEN - this is provided when a resource registers to be a broker to the MGX registry - it provides 
write/edit access to the registry for datasets loaded by that broker.
- SOURCE_ENDPOINT - the web view within the resource where you can view the loaded datasets, it should should be a 
long-term stable url that follows a standard format when provided a source ID. e.g. for EMBL-EBI's MGnify: https://www.ebi.ac.uk/metagenomics/analyses/{}
- SOURCE_PATTERN - a regular expression pattern used to validate the provided source IDs.
- PUBLIC_CHECK_ENDPOINT - an optional additional endpoint that can be provided to check if a dataset is public (for cases 
where the set of mappings include private data). This ensures only public data are loaded into the registry.

#### Information about the mappings

This section requests information about how the mappings between the source ID and the INSDC ID are 
formatted:

- MAPPINGS_DOWNLOAD - The url where the mappings are held.
- MAPPINGS_LOCAL - The mappings are downloaded locally before being loaded, this specifies the local file 
for the downloaded mappings.
- MAPPINGS_FORMAT - The format of the mappings - valid options are currently 'xlsx', 'csv' or 'tsv'
- MAPPINGS_HEADER - A boolean value whether the mappings have a header line that requires skipping before loading datasets.
- SOURCE_ID_COLUMN - The column index for the source analysis IDs within the mappings.
- INSDC_ID_COLUMN - The column index for the INSDC IDs within the mappings.

#### Other required metadata

This section is to provide the additional metadata required to describe Datasets. This script describes all datasets 
with the same additional metadata.

- METHODS - Methods that were used to derive the source ID to INSDC ID mappings, list all that apply:

```
hash_of_sequence
kmer_profile
taxonomy_signature
functional_signature
gps_coordinaties
biome
other_metadata
```

- CONFIDENCE - The confidence of the dataset to sequence mappings - valid options are:

```
full
high
medium
low
```

## Usage

```
python bulkLoadDatasets.py
```