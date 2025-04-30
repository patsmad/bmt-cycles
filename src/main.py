import click
from flask import Flask, request
from flask_cors import CORS
from util.config import Config


config = Config()
app = Flask(__name__)
CORS(app)

# api: API = api_builder.build()
# db_io: DBIO = db_io_builder.build()
# poster_fetcher: PosterFetcher = poster_fetcher_builder.build()


@app.route('/wiki/', methods=['GET'])
@config.api_check
def wiki() -> list[dict]:
    wiki_link: str = request.args.get('link')
    # TODO: Check that link is proper wiki link, pull out stub, and recast into en.wikipedia link
    return []

@click.group()
def cli():
    pass

@click.command()
def server():
    app.run(debug=True)

cli.add_command(server)

if __name__ == '__main__':
    cli()
