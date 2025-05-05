import click
from flask import Flask, request
from flask_cors import CORS

from src.scraping import imdb_db
from src.api import api, wiki
from util.config import Config


config = Config()
app = Flask(__name__)
CORS(app)

utilities = api.CompletionistUtilities.new()

@app.route('/wiki/', methods=['GET'])
@config.api_check
def wiki_get() -> list[dict]:
    wiki_link: str = request.args.get('link')
    film_data = wiki.WikiSource(wiki_link, utilities).get_film_data()
    return [f.to_json() for f in film_data]

@click.group()
def cli() -> None:
    pass

@click.command()
def update_imdb_data() -> None:
    imdb_db.recreate_tables()

@click.command()
def server() -> None:
    app.run(debug=True)

cli.add_command(update_imdb_data)
cli.add_command(server)

if __name__ == '__main__':
    cli()
