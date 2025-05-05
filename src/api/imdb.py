import sqlite3
from src.util.util_io import data_path
from typing import List

class IMDBDB:
    ratings_join_str = ("SELECT t.id, t.title, t.year, r.rating, r.votes, t.genres "
                        "FROM imdb_title t LEFT JOIN imdb_ratings r ON t.id = r.id "
                        "WHERE r.rating IS NOT NULL and t.id IN {}")

    def get_con(self) -> sqlite3.Connection:
        return sqlite3.connect(f'{data_path}/data/imdb.db')

    def get_ratings_votes(self, links: List[str]) -> dict:
        with self.get_con() as con:
            link_str = '(\"{}\")'.format('\",\"'.join([a.split('/title/')[1].split('/')[0] for a in links]))
            data = con.execute(self.ratings_join_str.format(link_str))
            return {'https://www.imdb.com/title/{}/'.format(datum[0]): {
                'title': datum[1],
                'year': datum[2],
                'rating': float(datum[3]),
                'votes': int(datum[4]),
                'genres': datum[5].split(',') if datum[5] else []
            } for datum in data}
