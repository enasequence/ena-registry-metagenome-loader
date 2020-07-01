#
# bulkLoadDatasets.py
#
#
import argparse
import csv
import time
import traceback
import sys
import pandas
import pandas.errors as pe
import requests
import requests.exceptions as re
import logging
from retry import retry

import settings


def set_parser():
    """Set and return the argument parser."""
    parser = argparse.ArgumentParser(prog='loadDatasets',
                                     description='Downloads INSDC ID to source'
                                                 ' ID mappings and loads '
                                                 'datasets into the Metagenome'
                                                 ' Exchange Registry')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 1.0.0')
    return parser


@retry(exceptions=re.RequestException, tries=3, delay=1)
def get_file(url):
    """
    Get mappings from url and save as a local file
    :param url: url where mappings are presented
    """
    try:
        logging.info(f'Getting file from {url}')
        r = requests.get(url)
        r.raise_for_status()
        with open(settings.MAPPINGS_LOCAL, 'wb') as f:
            f.write(r.content)
    except re.HTTPError as e:
        logging.error("Error retrieving mappings: {0}".format(e))
        sys.exit(1)
    except IOError as e:
        logging.error("Error writing to local file: {0}".format(e))
        sys.exit(1)


def convert_to_tsv(file_location):
    """
    Convert local mappings file to tsv format
    :param file_location: location of mappings file
    """
    try:
        if settings.MAPPINGS_FORMAT == 'xlsx':
            file = pandas.read_excel(file_location)
            file.to_csv(file_location, sep="\t", index=False)
        elif settings.MAPPINGS_FORMAT == 'csv':
            file = pandas.read_csv(file_location)
            file.to_csv(file_location, sep="\t", index=False)
        elif settings.MAPPINGS_FORMAT != 'tsv':
            logging.error(f"File type not valid, must be tsv, csv or xlsx:"
                          f" {settings.MAPPINGS_FORMAT}")
            sys.exit(1)
    except pe.ParserError as e:
        logging.error("Error with file conversion: {0}".format(e))
        sys.exit(1)


def convert_into_dataset(file_row):
    """
    Convert a row from the mappings file and return an MGX registry dataset.
    :param file_row: single row from mappings file
    :return MGX registry dataset object
    """
    if settings.RUN_PATTERN.match(file_row[settings.INSDC_ID_COLUMN]) and \
            settings.SOURCE_PATTERN.match(file_row[settings.SOURCE_ID_COLUMN]):
        return {
            "brokerID": settings.BROKER_ID,
            "sourceID": file_row[settings.SOURCE_ID_COLUMN],
            "endPoint": settings.SOURCE_ENDPOINT.format(
                file_row[settings.SOURCE_ID_COLUMN]),
            "status": "public",
            "sequenceID": file_row[settings.INSDC_ID_COLUMN],
            "method": settings.METHODS,
            "confidence": settings.CONFIDENCE
        }
    else:
        logging.error(
            f'INSDC accession or source accession in invalid format: '
            f'{file_row[settings.INSDC_ID_COLUMN]} '
            f'| {file_row[settings.SOURCE_ID_COLUMN]}')


def is_not_in_registry_yet(dataset):
    """
    Check if a dataset is in the registry, return a boolean.
    :param dataset: MGX registry dataset object
    :return boolean: if the dataset is not in the registry yet
    """
    response = get_datasets(dataset["sequenceID"])
    if response.status_code != 200:
        logging.error(
            f'Could not retrieve existing datasets from provided '
            f'INSDC sequence ID: {response.json()}')
        return False
    datasetsInRegistry = response.json()
    if datasetsInRegistry["datasets"]:
        return not includes(datasetsInRegistry, dataset)
    else:
        return True


def includes(datasets, dataset):
    """
    Check if registry datasets contain a specific dataset, return boolean.
    :param datasets: List of datasets returned by MGX registry
    :param dataset: MGX registry dataset object
    :return boolean: if the dataset is in the list of registry datasets
    """
    for d in datasets["datasets"]:
        if d["sourceID"] == dataset["sourceID"]:
            logging.info(f"Dataset already exists in the registry: {d}")
            return True
    return False


@retry(exceptions=re.RequestException, tries=3, delay=1)
def get_datasets(insdc_id):
    """
    Retrieve datasets from registry using INSDC id, return http response.
    :param insdc_id: A valid INSDC run ID
    :return http response: response for retrieving registry datasets for run id
    """
    try:
        url = settings.MGX_GET.format(insdc_id)
        response = requests.get(url)
        return response
    except re.RequestException as e:
        logging.error("Error accessing MGX registry: {0}".format(e))


@retry(exceptions=re.RequestException, tries=3, delay=1)
def dataset_is_public(dataset):
    """
    Check if dataset is public at public check endpoint, return boolean.
    :param dataset: MGX registry dataset object
    :return boolean: if dataset is public at settings.PUBLIC_CHECK_ENDPOINT
    """
    if settings.PUBLIC_CHECK_ENDPOINT:
        url = settings.PUBLIC_CHECK_ENDPOINT.format(dataset["sourceID"])
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            logging.info('Dataset is not public within source resource')
            return False
    else:
        return True


@retry(exceptions=re.RequestException, tries=3, delay=1)
def post_dataset(dataset):
    """
    Post dataset to registry API.
    :param dataset: MGX registry dataset object
    """
    try:
        logging.info(f'Posting dataset to registry: {dataset["sequenceID"]}')
        apikey = 'mgx ' + settings.AUTHORISATION_TOKEN
        headers = {'Authorization': apikey}
        r = requests.post(settings.MGX_POST, json=dataset, headers=headers)
        r.raise_for_status()
        logging.info(f'Dataset posted to registry: {r.content}')
        time.sleep(1)
    except re.HTTPError as e:
        logging.error("HTTP Error posting dataset to MGX registry:"
                      " {0}".format(e))
    except re.RequestException as e:
        logging.error("Error posting dataset to MGX registry: {0}".format(e))


def print_error():
    """Prints error if exception is thrown."""
    logging.error('Something unexpected went wrong please try again.')
    logging.error(
        'If problem persists, please contact us at '
        'https://www.ebi.ac.uk/ena/browser/support for assistance.')


if __name__ == '__main__':
    parser = set_parser()
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    try:
        logging.info(f'Loading datasets into MGX registry for broker: '
                     f'{settings.BROKER_ID}')
        get_file(settings.MAPPINGS_DOWNLOAD)
        convert_to_tsv(settings.MAPPINGS_LOCAL)

        with open(settings.MAPPINGS_LOCAL, "r") as fd:
            rd = csv.reader(fd, delimiter="\t", quotechar='"')
            logging.info(f'Reading mappings file: {settings.MAPPINGS_LOCAL}')
            if settings.MAPPINGS_HEADER:
                next(rd)
            for row in rd:
                dataset = convert_into_dataset(row)
                if dataset is not None:
                    if is_not_in_registry_yet(dataset):
                        if dataset_is_public(dataset):
                            post_dataset(dataset)
                        else:
                            logging.info(f'Dataset not posted to registry: '
                                         f'{dataset}')
                    else:
                        logging.info(f'Dataset not posted to registry:'
                                     f' {dataset}')
                else:
                    logging.error(f'Could not generate dataset for '
                                  f'{row[settings.SOURCE_ID_COLUMN]}')
        logging.info('Completed loading')
        sys.exit(1)
    except Exception:
        traceback.print_exc()
        print_error()
        sys.exit(1)
