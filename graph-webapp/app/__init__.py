from flask import Flask, send_from_directory, render_template, request, make_response
from json import load
from uuid import uuid4
import requests
from time import time


def create_app():
    """ Application factory to create the app and be passed to workers """
    app = Flask(__name__)

    import logging
    logging.basicConfig(
        filename='./logs/flask.log',
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    app.config['SECRET_KEY'] = 'thisisthesecretkeyfortheflaskserver'
    #app.config['SESSION_TYPE'] = 'redis'

    server_ip = requests.get("http://ipinfo.io/ip").content.decode('utf-8')

    graphs = {}
    expiration = 300  # 5 minutes

    @app.route('/', methods=['GET', 'POST'])
    @app.route('/index', methods=['GET', 'POST'])
    def index():
        return "", 418  # render_template('/index.html', graphs=graphs)

    @app.route('/graph/<ID>', methods=['GET', 'POST'])
    def graph(ID):
        """
        Main graph display page.
        If in debug mode, serves raw source files.
        """
        return render_template('/graph.html', development=app.config['DEBUG'])

    @app.route('/help')
    def tutorial():
        """ Serve the tutorial page """
        return render_template("/help.html", development=app.config['DEBUG'])

    @app.route('/src/<path:path>', methods=['GET'])
    def source(path):
        """ Serve source files in development mode """
        if app.config['DEBUG']:
            return send_from_directory("src", path)
        else:
            return "", 418

    @app.route('/create_graph', methods=['GET'])
    def create_graph():
        """ receive graph JSON from external source """
        logging.info("Received create_graph request")

        logging.info("Number of stored graphs: {}".format(len(list(graphs.keys()))))
        # remove expired graphs
        for ID in list(graphs.keys()):
            try:
                if time() - graphs[ID][1] > expiration:  # temporary until we implement sessions
                    logging.info("Removing graph ID: {}".format(ID))
                    del graphs[ID]
            except Exception as e:
                logging.error("Problem removing graph from dict: {}  {}".format(ID,e))
                continue

        ID = uuid4().hex  # generate random uuid
        logging.info("Created id: {}".format(ID))

        # store graph in index of all graphs with time created
        graphs[ID] = (request.json, time())
        logging.info("Stored graph")

        # return url to the graph display
        url = "http://{}:5000/graph/{}".format(server_ip, ID)
        logging.info("Generated URL and returning it: {}".format(url))

        return url

    @app.route('/get_graph/<ID>')
    def get_data(ID):
        """ Request graph JSON by ID """
        stuff = graphs.get(ID)
        if stuff is None:
            data = {
                "error": "Graph does not exist.",
                "message": "The graph (ID: {}) does not exist. If this graph was used previously, it may have expired since.".format(ID)}
            return data, 410
        return graphs[ID][0]


    return app

