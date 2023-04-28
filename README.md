# Python developer technical task
### Intro - Github Crawler

This document presents the technical task completed for the Github crawler. The crawler takes a JSON file as input and generates an output JSON file containing the expected data.

```commandline
usage: main.py [-h] [--input_file INPUT_FILE] [--output_file OUTPUT_FILE]
               [-append_output]

Github Crawler - IgnasiNouPlana28042023

optional arguments:
  -h, --help            show this help message and exit
  --input_file INPUT_FILE
                        Path to the input JSON file
  --output_file OUTPUT_FILE
                        Path to the output JSON file
  -append_output        If true retrieved data is appended to the output file
                        (if exists), by default output file is replaced

```

The web crawler is designed to handle three different input types: Repositories, Issues, and Wikis. An example of the input JSON file is provided. When retrieving Repository data, the output file is also appended with additional information about the repo's author and the languages used.

### Run main:

```
pip install -r requirements.txt
python main.py --input_file input.json
```
### Run tests:
```commandline
pip install -r requirements.txt
pytest
coverage run -m pytest
coverage report
```
### Run Dockerfile:

```commandline
 sudo docker build -t gitcrawler .
 sudo docker run -v $(pwd):/app gitcrawler --input_file input.json
```



- Example of the JSON file used:
```JSON
{
  "keywords": [
    "python",
    "django-rest-framework",
    "jwt"
  ],
  "proxies": [
    "194.126.37.94:8080",
    "13.78.125.167:8080",
    "5.189.184.6:80",
    "47.91.45.235:45554",
    "209.97.150.167:8080",
    "8.213.128.6:443",
    "172.104.117.89:80",
    "198.44.188.106:45787",
    "35.247.232.115:3129",
    "35.247.198.109:3129",
    "43.156.100.152:80",
    "116.203.139.170:8000"
  ],
  "type": "Repositories"
}


```
### Main features and structure

The application has the following main features and structure:

- It uses a rolling proxies system to retry the connection with all the available proxies in the input file.
- The history of processes are stored in a logging file called log.txt.
- The output files are named output_wikis.json, output_repos.json, and output_issues.json, depending on the type of data retrieved.
- The application has test coverage of 90%.
- The crawler uses BeautifulSoup mainly to scrape the data.
- Three different functions have been developed to scope the three different types of retrieved data: Wikis, Repos, and Issues. These functions are named `search_wikis(soup, base_url)`, `search_repo(soup, base_url)`, and `search_issues(soup, base_url)`, respectively.
- The project is divided into two python files: 
  - `main.py` that contains the main structure of the scraping.
  - `utils.py` that contains functions related the input and output json files and proxies + requests tools.
- To test the proxy functionality, we used the Mock module from pytest to obtain the expected responses for the requests. For testing the retrieval of HTML data, we created a dummy webpage and used mock in conjunction with BeautifulSoup.