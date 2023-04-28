import os
import json
import pytest
from utils import *
from unittest.mock import patch


def test_read_input_json():
    # Create a temporary JSON file
    test_data = {'keywords': ['test'], 'proxies': ['proxy'], 'type': 'repositories'}
    with open('test.json', 'w') as f:
        json.dump(test_data, f)

    # Test reading the JSON file
    keywords, proxies, type_ = read_input_json('test.json')
    assert keywords == test_data['keywords']
    assert proxies == test_data['proxies']
    assert type_ == test_data['type']

    # Test missing key in JSON file
    test_data.pop('type')
    with open('test.json', 'w') as f:
        json.dump(test_data, f)
    with pytest.raises(RuntimeError, match='One or more keys are missing or empty.'):
        read_input_json('test.json')

    # Test invalid JSON format
    with open('test.json', 'w') as f:
        f.write('invalid json')
    with pytest.raises(RuntimeError, match=f'Error: Invalid JSON format in test.json.'):
        read_input_json('test.json')

    # Test file not found
    with pytest.raises(RuntimeError, match=f'Error: File nonexistent_file.json not found.'):
        read_input_json('nonexistent_file.json')

    # Clean up the temporary file
    os.remove('test.json')


@pytest.fixture
def input_data():
    return [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 40}]


@pytest.fixture
def output_file(tmpdir):
    return os.path.join(tmpdir, 'test.json')


def test_save_json_without_append_output(input_data, output_file):
    output_file = save_json(input_data, output_file, 'info', False)

    assert os.path.exists(output_file)
    with open(output_file, 'r') as f:
        data = json.load(f)
    assert data == input_data


def test_save_json_with_append_output(input_data, output_file):
    save_json(input_data, output_file, 'info', False)
    new_data = [{'name': 'Charlie', 'age': 50}]
    output_file = save_json(new_data, output_file, 'info', True)

    assert os.path.exists(output_file)
    with open(output_file, 'r') as f:
        data = json.load(f)
    assert data == input_data + new_data


def test_save_json_with_invalid_output_file(input_data):
    with pytest.raises(ValueError):
        save_json(input_data, 'invalid', 'info', False)


@pytest.fixture
def proxies():
    return ['http://1.2.3.4:80']


def test_retrieve_data_success(proxies, mocker):
    url = 'https://example.com'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response_mock = mocker.Mock()
    response_mock.status_code = 200
    response_mock.text = 'Response data'

    request_mock = mocker.patch('requests.get', return_value=response_mock)

    result = get_proxy_and_response(proxies, url, headers)

    assert result == response_mock
    request_mock.assert_called_once_with(url, proxies={'https': proxies[0], 'http': proxies[0]}, headers=headers, timeout=5)


def test_retrieve_data_http_error(proxies, mocker):
    url = 'https://example.com'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response_mock = mocker.Mock()
    response_mock.status_code = 404
    response_mock.raise_for_status.side_effect = requests.exceptions.HTTPError

    request_mock = mocker.patch('requests.get', return_value=response_mock)

    with pytest.raises(RuntimeError):
        get_proxy_and_response(proxies, url, headers)

    request_mock.assert_called_with(url, proxies={'https': proxies[0], 'http': proxies[0]}, headers=headers, timeout=5)
    assert request_mock.call_count == len(proxies)


def test_retrieve_data_connection_error(proxies, mocker):
    url = 'https://example.com'
    headers = {'User-Agent': 'Mozilla/5.0'}

    request_mock = mocker.patch('requests.get', side_effect=requests.exceptions.ConnectionError)

    with pytest.raises(RuntimeError):
        get_proxy_and_response(proxies, url, headers)

    request_mock.assert_called_with(url, proxies={'https': proxies[0], 'http': proxies[0]}, headers=headers, timeout=5)
    assert request_mock.call_count == len(proxies)


def test_retrieve_data_timeout_error(proxies, mocker):
    url = 'https://example.com'
    headers = {'User-Agent': 'Mozilla/5.0'}

    request_mock = mocker.patch('requests.get', side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError):
        get_proxy_and_response(proxies, url, headers)

    request_mock.assert_called_with(url, proxies={'https': proxies[0], 'http': proxies[0]}, headers=headers, timeout=5)
    assert request_mock.call_count == len(proxies)


def test_retrieve_data_request_exception(proxies, mocker):
    url = 'https://example.com'
    headers = {'User-Agent': 'Mozilla/5.0'}

    request_mock = mocker.patch('requests.get', side_effect=requests.exceptions.RequestException)

    with pytest.raises(RuntimeError):
        get_proxy_and_response(proxies, url, headers)

    request_mock.assert_called_with(url, proxies={'https': proxies[0], 'http': proxies[0]}, headers=headers, timeout=5)
    assert request_mock.call_count == len(proxies)


def test_get_response_invalid_type():

    # Test invalid input
    type_ = "invalid_type"
    query = "myquery"
    proxies = {"https": "https://myproxy.com"}
    headers = {"User-Agent": "My User Agent"}
    base_url = "https://example.com"
    with pytest.raises(ValueError):
        get_response(type_, query, proxies, headers, base_url)

