from bs4 import BeautifulSoup
import argparse
from tqdm import tqdm
from utils import *
import logging
import colorlog
log = logging.getLogger("retrieve_github")
log.setLevel(logging.DEBUG)
log_file_name = f"log.txt"
if os.path.exists(log_file_name):
    os.remove(log_file_name)
fileHandler = logging.FileHandler(log_file_name)
handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
)
log.addHandler(handler)
log.addHandler(fileHandler)


def get_extra_info(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    languages = []
    percentages = []

    h2_element = soup.find("h2", string="Languages")
    div_element = h2_element.parent
    if div_element:
        for item in soup.find_all('li', class_='d-inline'):
            # find the <span> element containing the language and extract the text
            language_span = item.find('span', class_='color-fg-default text-bold mr-1')
            if language_span:
                language = language_span.get_text(strip=True)
                percentage = language_span.find_next().string
                languages.append(language)
                percentages.append(percentage)
    return languages, percentages


def search_repo(soup, base_url):
    urls = []
    owners = []
    repo_list = soup.find("ul", class_="repo-list")
    if repo_list:
        repos = repo_list.find_all("li")
        for repo in tqdm(repos, desc="Retrieving repos info"):
            a_tag = repo.find("a")
            repo_url = base_url + a_tag["href"]
            owner = a_tag["href"].split('/')[1]
            owners.append(owner)
            urls.append(repo_url)
        return owners, urls
    else:
        log.error(f"Your search did not match any repositories.")
        raise RuntimeError(f"Your search did not match any repositories.")


def search_issues(soup, base_url):
    issues_info = []
    issue_list = soup.find('div', {'id': 'issue_search_results'})
    issues = issue_list.find_all('a', {'class': 'Link--muted color-fg-muted'})
    for issue in tqdm(issues, desc="Retrieving issues info"):
        dict_issues = {}
        issue_number = issue.get_text(strip=True)
        issue_url = base_url + issue.get("href") + issue_number.replace('#', '/')
        dict_issues['url'] = issue_url
        issues_info.append(dict_issues)
    return issues_info


def search_wikis(soup, base_url):
    wikis_info = []
    wikis_list = soup.find('div', {'id': 'wiki_search_results'})
    for wikis in tqdm(wikis_list.find_all('div', class_='f4 text-normal'), desc="Retrieving wikis info"):
        dict_issues = {}
        wiki = wikis.find('a')
        link = wiki.get('href')
        wikis_url = base_url + link
        dict_issues['url'] = wikis_url
        wikis_info.append(dict_issues)
    return wikis_info


def get_extra(repos, owners, proxies, headers):
    repo_info = []
    for repo_url, owner in zip(repos, owners):
        repo_dict = {}
        log.info(f"Requesting info from: {repo_url}")
        response = get_proxy_and_response(proxies, repo_url, headers)
        languages, percentages = get_extra_info(response)
        # output dict
        repo_dict["url"] = repo_url
        extra_dict = {}
        extra_dict["owner"] = owner
        extra_dict["language_stats"] = {}
        for lan, per in zip(languages, percentages):
            extra_dict["language_stats"][lan] = float(per.replace("%", ""))
        repo_dict['extra'] = extra_dict
        repo_info.append(repo_dict)
    return repo_info


def search(query, proxies, type_):
    base_url = "https://github.com"
    headers = {'User-Agent': 'Mozilla/5.0'}

    # Retrieve info:
    if type_.lower() in ["repositories", "issues", "wikis"]:
        # 3 different retrievers since the requested data vary a lot.
        response = get_response(type_, query, proxies, headers, base_url)
        soup = BeautifulSoup(response.content, "html.parser")
        if type_.lower() == "repositories":
            owners, urls = search_repo(soup, base_url)
            list_repo = get_extra(urls, owners, proxies, headers)
            return list_repo
        elif type_.lower() == "issues":
            list_issues = search_issues(soup, base_url)
            return list_issues
        elif type_.lower() == "wikis":
            list_wikis = search_wikis(soup, base_url)
            return list_wikis
    else:
        raise ValueError(f"Invalid type_: {type_}")


def main(): # pragma: no cover

    parser = argparse.ArgumentParser(description='Github Crawler - IgnasiNouPlana28042023')
    parser.add_argument('--input_file', type=str, help='Path to the input JSON file', default='input.json')
    parser.add_argument('--output_file', type=str, help='Path to the output JSON file', default='output.json')
    parser.add_argument('-append_output', action='store_true', help='If true retrieved data is appended to the output file (if exists), by default output file is replaced')
    args = parser.parse_args()
    keywords, proxies, type_ = read_input_json(args.input_file)
    retrieved_info = search('+'.join(keywords), proxies, type_)
    output_file = save_json(retrieved_info, args.output_file, type_, args.append_output)
    log.info(f"SUCCESS: Output file saved: {output_file}")


if __name__ == '__main__':
    main()
