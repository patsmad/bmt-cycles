from src.model.film_data import FilmData
from src.scraping.wikidata import WikiDataQueries
from src.api.imdb import IMDBDB
from src.util.logger import Logger
from typing import Dict, List, Self

class CompletionistUtilities:
    def __init__(self, queries: WikiDataQueries, db: IMDBDB, logger: Logger) -> None:
        self.queries = queries
        self.db = db
        self.logger = logger

    @classmethod
    def new(cls) -> Self:
        logger = Logger()
        return CompletionistUtilities(
            WikiDataQueries(logger),
            IMDBDB(),
            logger
        )

class Source:
    def __init__(self, utilities: CompletionistUtilities) -> None:
        self.utilities = utilities

    def get_films(self) -> Dict[str, str]:
        return {}

    def get_film_data(self) -> List[FilmData]:
        films = self.get_films()
        rv = self.utilities.db.get_ratings_votes(list(films.values()))
        film_data = []
        for name, link in films.items():
            film_data.append(FilmData(name, link, rv.get(link, {})))
        return film_data
