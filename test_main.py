import pytest
from bs4 import BeautifulSoup
from requests import Response

from main import *


@pytest.fixture
def mock_response():
    mock_response = Response()
    mock_response._content = b'''
    <html>
    <head></head>
    <body>
        <h2>Languages</h2>
        <div>
            <li class="d-inline">
                <span class="color-fg-default text-bold mr-1">Python</span>
                <span>60%</span>
            </li>
            <li class="d-inline">
                <span class="color-fg-default text-bold mr-1">JavaScript</span>
                <span>40%</span>
            </li>
        </div>
    </body>
    </html>
    '''
    return mock_response


def test_get_extra_info(mock_response):
    expected_languages = ['Python', 'JavaScript']
    expected_percentages = ['60%', '40%']

    languages, percentages = get_extra_info(mock_response)

    assert languages == expected_languages
    assert percentages == expected_percentages


@pytest.fixture
def sample_soup():
    html = '''
        <html>
            <body>
                <div id="issue_search_results">
                    <a class="Link--muted color-fg-muted" data-hovercard-type="repository" data-hovercard-url="/wallabag/wallabag/hovercard" href="/wallabag/wallabag/issues">#1</a>
                    <a class="Link--muted color-fg-muted" data-hovercard-type="repository" data-hovercard-url="/wallabag/wallabag/hovercard" href="/wallabag/wallabag/issues">#2</a>
                    <a class="Link--muted color-fg-muted" data-hovercard-type="repository" data-hovercard-url="/wallabag/wallabag/hovercard" href="/wallabag/wallabag/issues">#3</a>
                </div>
            </body>
        </html>
    '''
    return BeautifulSoup(html, 'html.parser')


def test_search_issues(sample_soup):
    base_url = 'https://example.com'
    issues_info = search_issues(sample_soup, base_url)

    assert len(issues_info) == 3

    assert issues_info[0]['url'] == 'https://example.com/wallabag/wallabag/issues/1'
    assert issues_info[1]['url'] == 'https://example.com/wallabag/wallabag/issues/2'
    assert issues_info[2]['url'] == 'https://example.com/wallabag/wallabag/issues/3'


@pytest.fixture
def sample_soup2():
    html = '''
        <html>
            <body>
                <div id="wiki_search_results">
                    <div class="f4 text-normal">
                        <a data-hydro-click='{"event_type":"search_result.click","payload":{"page_number":1,"per_page":10,"query":"openstack css","result_position":1,"click_id":10041081,"result":{"id":10041081,"global_relay_id":"MDEwOlJlcG9zaXRvcnkxMDA0MTA4MQ==","model_name":"Repository","url":"https://github.com//CCI-MOC/moc-public/wiki/Debugging-the-installed-version-of-Horizon"},"originating_url":"https://github.com/search?q=openstack+css&amp;type=Wikis","user_id":null}}' data-hydro-click-hmac="7ddc4c79c4085e76aba4b2b783fe4fa1aa30f0f12e16203a510abbda9868779f" href="/CCI-MOC/moc-public/wiki/Debugging" title="Debugging the installed version of Horizon">Debugging the installed version of Horizon</a>
                    </div>
                    <div class="f4 text-normal">
                        <a data-hydro-click='{"event_type":"search_result.click","payload":{"page_number":1,"per_page":10,"query":"openstack css","result_position":1,"click_id":10041081,"result":{"id":10041081,"global_relay_id":"MDEwOlJlcG9zaXRvcnkxMDA0MTA4MQ==","model_name":"Repository","url":"https://github.com//CCI-MOC/moc-public/wiki/Debugging-the-installed-version-of-Horizon"},"originating_url":"https://github.com/search?q=openstack+css&amp;type=Wikis","user_id":null}}' data-hydro-click-hmac="7ddc4c79c4085e76aba4b2b783fe4fa1aa30f0f12e16203a510abbda9868779f" href="/CCI-MOC/moc-public/wiki/the-installed" title="Debugging the installed version of Horizon">Debugging the installed version of Horizon</a>
                    </div>
                    <div class="f4 text-normal">
                        <a data-hydro-click='{"event_type":"search_result.click","payload":{"page_number":1,"per_page":10,"query":"openstack css","result_position":1,"click_id":10041081,"result":{"id":10041081,"global_relay_id":"MDEwOlJlcG9zaXRvcnkxMDA0MTA4MQ==","model_name":"Repository","url":"https://github.com//CCI-MOC/moc-public/wiki/Debugging-the-installed-version-of-Horizon"},"originating_url":"https://github.com/search?q=openstack+css&amp;type=Wikis","user_id":null}}' data-hydro-click-hmac="7ddc4c79c4085e76aba4b2b783fe4fa1aa30f0f12e16203a510abbda9868779f" href="/CCI-MOC/moc-public/wiki/Horizon" title="Debugging the installed version of Horizon">Debugging the installed version of Horizon</a>
                    </div>
                </div>
            </body>
        </html>
    '''
    return BeautifulSoup(html, 'html.parser')


def test_search_wikis(sample_soup2):
    base_url = 'https://example.com'
    wikis_info = search_wikis(sample_soup2, base_url)

    assert len(wikis_info) == 3

    assert wikis_info[0]['url'] == 'https://example.com/CCI-MOC/moc-public/wiki/Debugging'
    assert wikis_info[1]['url'] == 'https://example.com/CCI-MOC/moc-public/wiki/the-installed'
    assert wikis_info[2]['url'] == 'https://example.com/CCI-MOC/moc-public/wiki/Horizon'


def test_invalid_type():
    proxies = {"https": "https://myproxy.com"}
    with pytest.raises(ValueError) as exc_info:
        search("some query", proxies, "invalid_type")
    assert str(exc_info.value) == "Invalid type_: invalid_type"

def test_search_repo():
    soup = BeautifulSoup("""
    <ul class="repo-list">
        <li>
            <a href="/abhirawat7/Astack-OpenStack-PythonFlask-"></a>
        </li>
        <li>
            <a href="/michealbalogun/Horizon-dashboard"></a>
        </li>
        <li>
            <a href="/airavata-courses/IU-Witcher-2020"></a>
        </li>
    </ul>
    """, 'html.parser')
    base_url = "https://github.com"
    owners, urls = search_repo(soup, base_url)
    assert owners == ['abhirawat7', 'michealbalogun', 'airavata-courses']
    assert urls == ['https://github.com/abhirawat7/Astack-OpenStack-PythonFlask-',
                    'https://github.com/michealbalogun/Horizon-dashboard',
                    'https://github.com/airavata-courses/IU-Witcher-2020']


def test_search_repo_no_results():
    soup = BeautifulSoup('<html></html>', 'html.parser')
    base_url = 'https://github.com/'
    with pytest.raises(RuntimeError) as excinfo:
        search_repo(soup, base_url)
    assert str(excinfo.value) == "Your search did not match any repositories."


