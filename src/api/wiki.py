from bs4 import BeautifulSoup as BS
from src.api.api import CompletionistUtilities, Source
from src.util.request import soupifyURL
import re
from typing import Dict, List

class WikiSource(Source):
    def __init__(self, link: str, utilities: CompletionistUtilities) -> None:
        super().__init__(utilities)
        self.links, self.soups = self.get_links(link)
        self.wiki_links = WikiSource.filter_links(self.soups)

    def log(self, s: str) -> None:
        #TODO: Add logger (to stream) from Source
        print(s)

    @staticmethod
    def get_approximate_number(soup) -> int:
        pattern = r'The following [0-9\,]{1,} pages are in this category, out of (approximately )?[0-9\,]{1,} total'
        pattern_match = re.search(pattern, soup.text)
        if pattern_match:
            second_part = pattern_match.group().split('pages are in this category, out of')[1]
            return int(re.search(r'[0-9,]{1,}', second_part).group().replace(',', ''))
        else:
            return 0

    def get_links(self, link: str) -> (List[str], List[BS]):
        links = [link]
        soups = [soupifyURL(link)]
        approximate_number = WikiSource.get_approximate_number(soups[-1])
        maybe_next_page = [a['href'] for a in soups[-1].find_all('a', href=True) if a.text == 'next page']
        page = 1
        while len(maybe_next_page) > 0:
            page += 1
            self.log('Fetching page {} ({} total items)'.format(page, approximate_number))
            links.append('https://en.wikipedia.org{}'.format(maybe_next_page[0]))
            soups.append(soupifyURL(links[-1]))
            maybe_next_page = [a['href'] for a in soups[-1].find_all('a', href=True) if a.text == 'next page']
        return links, soups

    @staticmethod
    def ignored_links(link: str) -> bool:
        return '/wiki/Special:' not in link and \
            '/wiki/Wikipedia:' not in link and \
            '/wiki/Category_talk:' not in link and \
            '/wiki/File:' not in link

    @staticmethod
    def filter_links(soups: List[BS]) -> list[str]:
        all_links = [a['href'] for soup in soups for a in soup.find_all('a', href=True) if WikiSource.ignored_links(a['href'])]
        return list(set('https://en.wikipedia.org{}'.format(a) for a in all_links if a[:6] == '/wiki/'))

    def get_raw_dict(self, links: List[str]) -> Dict[str, str]:
        return self.utilities.queries.getIMDBLinks(links)

    @staticmethod
    def confirm_films(raw_dict: Dict[str, str]) -> Dict[str, str]:
        return {k: v for k, v in raw_dict.items() if '/tt' in v}

    def get_redirect_links(self, filtered_links: List[str]) -> List[str]:
        redirect_links = []
        self.log('Finding redirects for {} films'.format(len(filtered_links)))
        for link in filtered_links:
            try:
                self.log(link)
                link_soup = soupifyURL('{}?redirect=no'.format(link))
                maybeRedirectMsg = link_soup.find_all('div', 'redirectMsg')
                if len(maybeRedirectMsg) > 0:
                    redirect_links.append('https://en.wikipedia.org{}'.format(maybeRedirectMsg[0].find('a')['href']))
            except:
                self.log("Skipping {}".format(link))
        return redirect_links

    def get_films(self) -> Dict[str, str]:
        self.log('Found {} wiki links'.format(len(self.wiki_links)))
        raw_dict = self.get_raw_dict(self.wiki_links)
        films = WikiSource.confirm_films(raw_dict)
        self.log('Confirmed {} films'.format(len(films)))
        redirect_links = self.get_redirect_links([a for a in self.wiki_links if a not in raw_dict])
        redirect_dict = self.get_raw_dict(redirect_links)
        self.log('Found Redirected for {} films'.format(len(redirect_dict)))
        films.update(WikiSource.confirm_films(redirect_dict))
        self.log('Found {} total links'.format(len(films)))
        return films
