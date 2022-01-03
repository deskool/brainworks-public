# BRAINWORKS

## Graph API Webserver



## About

This directory contains the full code for the Python Flask web application used to host the graph API of the [visualization layer](../documentation/visualization-layer.md).



## Hosting Instructions

To host the API publicly, 

1. execute `run.sh` on the remote server (port 5000 must be open).
2. To reload the app, execute `reload.sh`.
3. To force quit the app, execute `quit.sh`.

To compile all javascript into a single minified asset, execute `npm run build` (must have all node modules installed). Usage documentation and examples can be found in `documentation/`

