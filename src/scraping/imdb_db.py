import sqlite3
from src.util.request import downloadFile
from src.util.util_io import data_path, make_dirs, readTSV, streamTSV, unzipGZFile
from typing import List, Set

class DBTableCreator:
    chunk_size = 1000
    db_name = 'imdb'

    def get_con(self) -> sqlite3.Connection:
        return sqlite3.connect('{}/data/{}.db'.format(data_path, self.db_name))

    def stringify(self, value: str) -> str:
        return '\"{}\"'.format(value.replace('"', '""'))

    def nullable(self, value: str) -> str:
        return self.stringify(value) if value != '\\N' else 'null'

    def insert_in_chunks(self, base_str: str, rows: List[str]) -> None:
        with self.get_con() as con:
            chunks = len(rows) // self.chunk_size + 1
            for chunk in [rows[self.chunk_size * i:self.chunk_size * (i + 1)] for i in range(chunks)]:
                if len(chunk) > 0:
                    con.execute(base_str.format('),('.join([', '.join(row) for row in chunk])))

class DBTitleTableCreator(DBTableCreator):
    def recreate_table(self) -> None:
        with self.get_con() as con:
            con.execute("DROP TABLE IF EXISTS imdb_title")
            con.execute("CREATE TABLE IF NOT EXISTS imdb_title ("
                        "id STRING NOT NULL, "
                        "title STRING NOT NULL, "
                        "alternate_title STRING,"
                        "year INTEGER, "
                        "runtime INTEGER, "
                        "genres STRING)")

    def transform_table_row(self, row: str, headers: str) -> tuple:
        split_row = row.strip().split('\t')
        if len(split_row) == 9 and split_row[1] in ['movie', 'video', 'tvMovie'] and 'Adult' not in split_row[8]:
            title = self.stringify(split_row[2])
            alternate_title_basic = self.stringify(split_row[3])
            alternate_title_aka = self.aka_map.get(split_row[0])
            saved_alternate_title = 'null'
            if title != alternate_title_basic:
                saved_alternate_title = alternate_title_basic
            elif alternate_title_aka is not None:
                saved_alternate_title = alternate_title_aka
            return (
                self.stringify(split_row[0]),
                title,
                saved_alternate_title,
                self.nullable(split_row[5]),
                self.nullable(split_row[7]),
                self.nullable(split_row[8])
            )

    def filter_akas(self, row: str, headers: str) -> tuple:
        split_row = row.strip().split('\t')
        if len(split_row) >= 7 and split_row[3] == 'US' and split_row[6] == 'short title':
            return (
                split_row[0],
                self.stringify(split_row[2])
            )

    def remake_table(self) -> None:
        self.recreate_table()
        self.aka_map = {a[0]: a[1] for a in streamTSV('data/data_dumps/title.akas.tsv', self.filter_akas)}
        rows = streamTSV('data/data_dumps/title.basics.tsv', self.transform_table_row)

        print('Inserting {} rows'.format(len(rows)))
        base_str = 'INSERT INTO imdb_title (id, title, alternate_title, year, runtime, genres) VALUES ({})'
        self.insert_in_chunks(base_str, rows)

class DBRatingsTableCreator(DBTableCreator):
    def __init__(self) -> None:
        self.valid_ids = self.get_valid_ids()

    def recreate_table(self) -> None:
        with self.get_con() as con:
            con.execute("DROP TABLE IF EXISTS imdb_ratings")
            con.execute("CREATE TABLE IF NOT EXISTS imdb_ratings ("
                        "id STRING NOT NULL, "
                        "rating DOUBLE, "
                        "votes INTEGER)")
            con.execute("CREATE INDEX film_id_idx ON imdb_ratings(id)")

    def transform_table_row(self, row: str, headers: str) -> tuple:
        split_row = row.strip().split('\t')
        if len(split_row) == 3 and split_row[0] in self.valid_ids:
            return (
                self.stringify(split_row[0]),
                self.nullable(split_row[1]),
                self.nullable(split_row[2])
            )

    def remake_table(self) -> None:
        self.recreate_table()
        rows = streamTSV('data/data_dumps/title.ratings.tsv', self.transform_table_row)

        print('Inserting {} rows'.format(len(rows)))
        base_str = 'INSERT INTO imdb_ratings (id, rating, votes) VALUES ({})'
        self.insert_in_chunks(base_str, rows)

    def get_valid_ids(self) -> Set[str]:
        with self.get_con() as con:
            return set([row[0] for row in con.execute("SELECT id FROM imdb_title")])

class IMDBDataDump:
    def __init__(self, fname: str) -> None:
        self.fname = fname

    def fetch_dump(self) -> None:
        make_dirs('data/data_dumps')
        downloadFile('https://datasets.imdbws.com/' + self.fname, 'data/data_dumps/' + self.fname)
        unzipGZFile('data/data_dumps/' + self.fname)

def recreate_tables() -> None:
    IMDBDataDump('title.basics.tsv.gz').fetch_dump()
    IMDBDataDump('title.akas.tsv.gz').fetch_dump()
    main_db = DBTitleTableCreator()
    print("Making Main Table")
    main_db.remake_table()
    print("Main Table Created")
    IMDBDataDump('title.ratings.tsv.gz').fetch_dump()
    rating_db = DBRatingsTableCreator()
    print("Making Ratings Table")
    rating_db.remake_table()
    print("Rating Rating Created")
