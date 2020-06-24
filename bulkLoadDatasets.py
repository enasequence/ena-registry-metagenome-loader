#
# bulkLoadDatasets.py
#
#
import argparse
import csv
import time
import traceback
import re
import sys
import pandas
import requests
import logging

import configmgrast as config


def set_parser():
    parser = argparse.ArgumentParser(prog='loadDatasets',
                                     description='Downloads INSDC ID to source ID mappings and loads datasets '
                                                 'into the Metagenome Exchange Registry')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0')
    return parser


run_pattern = re.compile('^[EDS]RR[0-9]{6,7}$')
source_pattern = re.compile(config.SOURCE_PATTERN)
MGX_GET = 'https://wwwdev.ebi.ac.uk/ena/registry/metagenome/api/sequences/{}/datasets'
MGX_POST = 'https://wwwdev.ebi.ac.uk/ena/registry/metagenome/api/admin/datasets'


def get_file(url):
    try:
        logging.info(f'Getting file from {url}')
        r = requests.get(url)
        with open(config.MAPPINGS_LOCAL, 'wb') as f:
            f.write(r.content)
        return True
    except Exception as e:
        logging.error("Error with request: {0}".format(e))
        return False


def convert_to_tsv(file_location):
    try:
        if config.MAPPINGS_FORMAT == 'tsv':
            return True
        if config.MAPPINGS_FORMAT == 'xlsx':
            file = pandas.read_excel(file_location)
            file.to_csv(file_location, sep="\t", index=False)
            return True
        if config.MAPPINGS_FORMAT == 'csv':
            file = pandas.read_csv(file_location)
            file.to_csv(file_location, sep="\t", index=False)
            return True
        else:
            return False
    except Exception as e:
        logging.error("Error with file conversion: {0}".format(e))
        return False

def convert_into_dataset(file_row):
    if is_run_accession(file_row[config.INSDC_ID_COLUMN]) and is_source_accession(file_row[config.SOURCE_ID_COLUMN]):
        return {
            "brokerID": config.BROKER_ID,
            "sourceID": file_row[config.SOURCE_ID_COLUMN],
            "endPoint": config.SOURCE_ENDPOINT.format(file_row[config.SOURCE_ID_COLUMN]),
            "status": "public",
            "sequenceID": file_row[config.INSDC_ID_COLUMN],
            "method": config.METHODS,
            "confidence": config.CONFIDENCE
        }
    else:
        logging.error(f'INSDC accession or source accession in invalid format: {file_row[config.INSDC_ID_COLUMN]} '
                      f'| {file_row[config.SOURCE_ID_COLUMN]}')
        return None


def is_run_accession(insdc_id):
    return run_pattern.match(insdc_id)


def is_source_accession(source_id):
    return source_pattern.match(source_id)


def is_not_in_registry_yet(dataset):
    response = get_datasets(dataset["sequenceID"])
    if response.status_code != 200:
        logging.error(f'Could not retrieve existing datasets from provided INSDC sequence ID: {response.json()}')
        return False
    datasetsInRegistry = response.json()
    if "datasets" in datasetsInRegistry:
        if datasetsInRegistry["datasets"]:
            if includes(datasetsInRegistry, dataset):
                return False
            else:
                return True
        else:
            return True
    else:
        logging.error(f"Could not retrieve datasets: {datasetsInRegistry}")
        return False


def includes(datasets, dataset):
    for d in datasets["datasets"]:
        if d["sourceID"] == dataset["sourceID"]:
            logging.info(f"Dataset already exists in the registry: {d}")
            return True
    return False


def get_datasets(insdc_id):
    try:
        url = MGX_GET.format(insdc_id)
        response = requests.get(url)
        return response
    except Exception as e:
        logging.error("Error accessing MGX registry: {0}".format(e))
        return None


def dataset_is_public(dataset):
    if config.PUBLIC_CHECK_ENDPOINT != '':
        url = config.PUBLIC_CHECK_ENDPOINT.format(dataset["sourceID"])
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            logging.info('Dataset is not public within source resource')
            return False
    else:
        return True


def post_dataset(dataset):
    try:
        logging.info(f'Posting dataset to registry: {dataset["sequenceID"]}')
        apikey = 'mgx ' + config.AUTHORISATION_TOKEN
        headers = {'Authorization': apikey}
        r = requests.post(MGX_POST, json=dataset, headers=headers)
        logging.info(f'Dataset not posted to registry: {r.content}')
        time.sleep(1)
    except Exception as e:
        logging.error("Error posting dataset to MGX registry: {0}".format(e))


def print_error():
    logging.error('Something unexpected went wrong please try again.')
    logging.error('If problem persists, please contact us at https://www.ebi.ac.uk/ena/browser/support for assistance.')


if __name__ == '__main__':
    parser = set_parser()
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    try:
        logging.info(f'Loading datasets into MGX registry for broker: {config.BROKER_ID}')
        get_file(config.MAPPINGS_DOWNLOAD)
        convert_to_tsv(config.MAPPINGS_LOCAL)

        with open(config.MAPPINGS_LOCAL) as fd:
            rd = csv.reader(fd, delimiter="\t", quotechar='"')
            logging.info(f'Reading mappings file: {config.MAPPINGS_LOCAL}')
            if config.MAPPINGS_HEADER:
                next(rd)
            for row in rd:
                dataset = convert_into_dataset(row)
                if dataset is not None:
                    if is_not_in_registry_yet(dataset):
                        if dataset_is_public(dataset):
                            post_dataset(dataset)
                        else:
                            logging.info(f'Dataset not posted to registry: {dataset}')
                    else:
                        logging.info(f'Dataset not posted to registry: {dataset}')
                else:
                    logging.error(f'Could not generate dataset for {row[config.SOURCE_ID_COLUMN]}')
        logging.info('Completed loading')
        sys.exit(1)
    except Exception:
        traceback.print_exc()
        print_error()
        sys.exit(1)
