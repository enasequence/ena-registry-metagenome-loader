# Information about the broker #
# ---------------------------- #
BROKER_ID = ''  # Registry provided broker ID
AUTHORISATION_TOKEN = ''  # Registry provided auth token
SOURCE_ENDPOINT = ''  # endpoint to view dataset in broker resource - where {} should be the unique source ID
SOURCE_PATTERN = ''  # regex pattern to validate source ID on loading
PUBLIC_CHECK_ENDPOINT = ''  # Public endpoint to check if a dataset is public - where {} should be the unique source ID

# Information about the mappings #
# ------------------------------ #
MAPPINGS_DOWNLOAD = ''  # Where to download the mappings from
MAPPINGS_LOCAL = ''  # Where to download the mappings to on the local file system
MAPPINGS_FORMAT = ''  # Format of the mappings - options are 'xlsx', 'csv' or 'tsv'
MAPPINGS_HEADER = True / False  # Whether the mappings have a header line
SOURCE_ID_COLUMN = 0  # The column index for the analysis IDs
INSDC_ID_COLUMN = 0  # The column index for the INSDC IDs

# Other required metadata #
# ----------------------- #
METHODS = ['other_metadata']  # methods used to derive dataset to sequence mappings
CONFIDENCE = 'full'  # confidence of the dataset to sequence mappings
