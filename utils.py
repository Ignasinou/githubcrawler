import copy
import requests
import random
import json
import os
import logging
from urllib.parse import urljoin
log = logging.getLogger("retrieve_github")
log.setLevel(logging.DEBUG)


def get_proxy_and_response(proxies, url, headers, params):
    proxies_temp = copy.copy(proxies)
    while proxies_temp:
        rand_int = random.randint(0, len(proxies_temp) - 1)
        rand_proxy = proxies_temp.pop(rand_int)  # Retrieve and remove the first proxy from the list
        proxy = {"https": rand_proxy,
                 "http": rand_proxy
                 }
        try:
            log.info(f"Trying request with the following proxy: {proxy}")
            response = requests.get(url, proxies=proxy, headers=headers, timeout=5, params=params)
            response.raise_for_status()
            log.info(f"Request SUCCESS! {url} {proxy}")
            return response
        except requests.exceptions.HTTPError as errh:
            log.error(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            log.error(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            log.error(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            log.error(f"Something went wrong: {err}")
    log.error(f"ERROR: All proxies failed")
    raise ValueError(f"ERROR: All proxies failed")


def get_response(type_, query, proxies, headers, base_url):

    if type_.lower() == "repositories" or type_.lower() == "issues" or type_.lower() == "wikis":
        url = urljoin(base_url, "/search?q=", query)
    else:
        raise ValueError("Invalid object type. Supported types are 'Repositories', 'Issues', and 'Wikis'.")

    response = get_proxy_and_response(proxies, url, headers, type_.lower())
    return response


def read_input_json(input_json):
    keywords = []
    proxies = []
    type_ = []
    try:
        with open(input_json, 'r') as f:
            data = json.load(f)
            keywords = data.get('keywords')
            proxies = data.get('proxies')
            type_ = data.get('type')
            if not all([keywords, proxies, type_]):
                raise RuntimeError('One or more keys are missing or empty.')

    except FileNotFoundError:
        log.error(f'Error: File {input_json} not found.')
        raise RuntimeError(f'Error: File {input_json} not found.')
    except json.JSONDecodeError:
        log.error(f'Error: Invalid JSON format in {input_json}.')
        raise RuntimeError(f'Error: Invalid JSON format in {input_json}.')
    return keywords, proxies, type_


def save_json(retrieved_info, output_file, type_, append_output):
    extension = output_file.split('/')[-1].split('.')[-1]
    if extension != 'json':
        raise ValueError
    output_file = output_file.split('.json')[0] + "_" + type_.lower() + ".json"
    if os.path.exists(output_file) and append_output:
        # Open the JSON file for reading
        with open(output_file, 'r') as outfile:
            existing_data = json.load(outfile)
            existing_data.extend(retrieved_info)
        with open(output_file, 'w') as outfile:
            json.dump(existing_data, outfile, indent=4)
    else:
        with open(output_file, "w") as outfile:
            json.dump(retrieved_info, outfile, indent=4)

    return output_file

