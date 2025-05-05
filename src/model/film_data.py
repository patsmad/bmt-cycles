
class FilmData:
    def __init__(self, name: str, link: str, rv: dict) -> None:
        self.name = name
        self.link = link
        self.title = rv.get('title')
        self.year = rv.get('year')
        self.rating = rv.get('rating')
        self.votes = rv.get('votes')
        self.genres = rv.get('genres', [])

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'link': self.link,
            'title': self.title,
            'year': self.year,
            'rating': self.rating,
            'votes': self.votes,
            'genres': self.genres
        }
