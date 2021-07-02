from setuptools import find_packages

import click
from flask.cli import AppGroup, with_appcontext

from starks.app import create_app
from starks.extensions import db


app = create_app(__name__)


def _import_models():
    packages = find_packages('./starks/modules')
    for each in packages:
        guess_module_name = 'starks.modules.%s.model' % each
        try:
            __import__(guess_module_name, globals(), locals())
            print('Find model:', guess_module_name)
        except ImportError:
            pass


@app.cli.command("syncdb")
@with_appcontext
def syncdb():
    _import_models()
    db.create_all()
    db.session.commit()
    print("Database created")


@app.cli.command("run")
def runserver():
    app.run(debug=True)
