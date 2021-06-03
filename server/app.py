from flask import Flask, request, jsonify

import logging

from .extensions import scheduler

import os

# https://github.com/viniciuschiele/flask-apscheduler/blob/master/examples/application_factory/__init__.py


def create_app():
    """Create a new app instance."""

    def is_debug_mode():
        """Get app debug status."""
        debug = os.environ.get("FLASK_DEBUG")
        if not debug:
            return os.environ.get("FLASK_ENV") == "development"
        return debug.lower() not in ("0", "false", "no")

    def is_werkzeug_reloader_process():
        """Get werkzeug status."""
        return os.environ.get("WERKZEUG_RUN_MAIN") == "true"

    # pylint: disable=W0621
    app = Flask(__name__)
    scheduler.init_app(app)

    logging.getLogger("apscheduler").setLevel(logging.INFO)

    # pylint: disable=C0415, W0611
    with app.app_context():

        # pylint: disable=W0611
        if is_debug_mode() and not is_werkzeug_reloader_process():
            pass
        else:
            from . import ranking  # noqa: F401
            scheduler.api_enabled = True
            scheduler.start()

        from . import search, equipment  # noqa: F401

        app.register_blueprint(search.s_bp)
        app.register_blueprint(equipment.eq_bp)

        return app


app = create_app()

if __name__ == "__main__":
    app.run()
