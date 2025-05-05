import requests
import time
from src.util.util_io import readJSON
from datetime import datetime
from typing import Dict, List

class WikiDataRequester:
    def __init__(self) -> None:
        self.headers = readJSON('config')['headers']
        self.last_request = None

    def wait(self) -> None:
        if self.last_request:
            wait_time = max(1.0 - (datetime.now() - self.last_request).total_seconds(), 0.0)
            if wait_time > 0.0:
                print("Waiting {} seconds".format(wait_time))
            time.sleep(wait_time)
        self.last_request = datetime.now()

    def getLimitedResponse(self, query: str) -> requests.Response:
        self.wait()
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
        return self.getLimitedResponseRetry(url, query, allowRetry=True)

    def getLimitedResponseRetry(self, url: str, query: str, allowRetry: bool) -> requests.Response:
        try:
            response = requests.get(url, params={'query': query, 'format': 'json'}, headers=self.headers)
            if response.status_code != 200:
                print('Non-200 Error code')
                raise RuntimeError
            return response
        except:
            if allowRetry:
                return self.getLimitedResponseRetry(url, query, allowRetry=False)
            else:
                raise RuntimeError

class WikiDataQueries:
    def __init__(self) -> None:
        self.requester = WikiDataRequester()

    # Input: a list of full wikipedia links (must be https)
    # Output: A dictionary of full wikipedia links to a dictionary defining the imdb link for each
    # NOTE: Only those with imdb links will be returned
    def getIMDBLinks(self, wikiLinks: List[str]) -> Dict[str, str]:
        allLinks = [link.split('#')[0] for link in wikiLinks]
        chunkedLinks = [allLinks[i * 50:(i + 1) * 50] for i in range((len(allLinks) - 1) // 50 + 1)]
        out = {}
        for linkChunk in chunkedLinks:
            query_str = '<' + '> <'.join(linkChunk) + '>'
            query = """
                SELECT
                  ?item ?itemLabel
                  ?article
                  ?imdb ?imdbLabel
                WHERE
                {{
                  ?article schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> .
                  ?item wdt:P345 ?imdb
                  VALUES ?article {{ {0} }}
                  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
                }}
            """.format(query_str)

            response = self.requester.getLimitedResponse(query)
            data = response.json()

            out.update({
                a['article']['value']: 'https://www.imdb.com/title/{}/'.format(a['imdb']['value'])
                for a in data['results']['bindings']
            })
        return out
