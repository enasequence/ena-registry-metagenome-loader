import re
from decouple import config, Csv

MGX_GET = 'https://wwwdev.ebi.ac.uk/ena/registry/metagenome/api/' \
          'sequences/{}/datasets'
MGX_POST = 'https://wwwdev.ebi.ac.uk/ena/registry/metagenome/api/' \
           'admin/datasets'

RUN_PATTERN = re.compile('^[EDS]RR[0-9]{6,7}$')
SOURCE_PATTERN = re.compile(config('SOURCE_PATTERN'))

BROKER_ID = config('BROKER_ID')
AUTHORISATION_TOKEN = config('AUTHORISATION_TOKEN')
SOURCE_ENDPOINT = config('SOURCE_ENDPOINT')
PUBLIC_CHECK_ENDPOINT = config('PUBLIC_CHECK_ENDPOINT', default='')

MAPPINGS_DOWNLOAD = config('MAPPINGS_DOWNLOAD')
MAPPINGS_LOCAL = config('MAPPINGS_LOCAL')
MAPPINGS_FORMAT = config('MAPPINGS_FORMAT', default='tsv')
MAPPINGS_HEADER = config('MAPPINGS_HEADER', cast=bool)
SOURCE_ID_COLUMN = config('SOURCE_ID_COLUMN', cast=int)
INSDC_ID_COLUMN = config('INSDC_ID_COLUMN', cast=int)

METHODS = config('METHODS', cast=Csv())
CONFIDENCE = config('CONFIDENCE')
