import click
from flask import Flask, request
from flask_cors import CORS

from src.runners import imdb
from util.config import Config


config = Config()
app = Flask(__name__)
CORS(app)


@app.route('/wiki/', methods=['GET'])
@config.api_check
def wiki() -> list[dict]:
    wiki_link: str = request.args.get('link')
    print(wiki_link)
    # TODO: Check that link is proper wiki link, pull out stub, and recast into en.wikipedia link
    return []

@click.group()
def cli():
    pass

@click.command()
def update_imdb_data():
    imdb.recreate_tables()

@click.command()
def server():
    app.run(debug=True)

cli.add_command(update_imdb_data)
cli.add_command(server)

if __name__ == '__main__':
    cli()
