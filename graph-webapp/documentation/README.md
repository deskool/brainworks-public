# Contents
- [Making a Call](#call)
- [Graph JSON Structure](#json_structure)
- [JSON Examples](#json_examples)

<section id="call"></section>

### Making a Call
To make a call to the API, send a GET request to `graph.scigami.org:5000/create_graph`, along with appropriate JSON data (outlined below).
The response will be a complete URL to the resulting graph page, which will be valid for a short period of time. 
This URL can be navigated to directly, or displayed in an HTML iframe. A sample webpage can be found in `simple_webpage.html`.

##### Example GET request to API made in python:
`url = requests.get("graph.scigami.org:5000/create_graph", json=json_data).content.decode()`


<section id="json_structure"></section>

### JSON STRUCTURE
Structure of the request content in python dictionary syntax ("json_data" in the code above):\
`{"graph: {}, "config": {}}`

- structure of the "graph" dict: `{"nodes": [], "edges": []}`
  - each node: `{"key": <string>, "attributes": {}}`
    - key: unique id for each node
    - attributes: `{"label": <string>, "x": <float>, "y": <float>, "size": <float>, "color": <string>, "data": {}}`
      - label: visible node label in the graph
      - x/y: x and y position of the node in the graph
      - size: radius of the node
      - color: hex code to color the node
      - data: all custom key-value pairs assigned to the node
  - each edge: `{"key": <string>, "source": <string>, "target", <string>, "attributes": {}}`
    - key: unique id for each node
    - source: unique id of the source node
    - target: unique id of the target node
    - attributes: `{"label": <string>, "size": <float>, "color": <string>, "data": {}}`
      - label: visible edge label in the graph
      - size: edge thickness
      - color: hex code to color the edge
      - data: all custom key-value pairs assigned to the edge

Note that, by default, all key-value pairs in the "data" object are the only custom values directly visible to the user.

- structure of the "config" dict: `{"maps": [], "settings": {}}`
  - each map: `{"dimension": <string>, "data": <string|[]>, "args": <string|{}>}`
    - dimension: name of the dimension to map the data to. Allowed values are: `"node_size", "node_color", "node_slider", "cluster", "edge_size", "edge_color", "edge_slider"`
    - data: key of the custom property assigned in the node "data" attribute.
      - if the dimension is `"cluster"`, then this is rather a list of data keys to order the clustering by
    - args: arguments dependent on the dimension type (only one of the following)
      - if dimension type is `"node_slider"`:
        - an optional string, the name of the slider.
      - if dimension type is continuous (i.e. size): `{"min": <float>, "max": <float>}`
        - min: minimum value of the dimension to map
        - max: maximum value of the dimension to map
      - if dimension type is categorical (color): 
        - keys are data key categories
        - values are dimension categories
  - (optional) settings: not yet implemented

<section id="json_examples"></section>

##### Examples of JSON data to send

Minimal example:
<pre>
{
  "graph": {
    "nodes": [{"key": "node_1"}, {"key": "node_2"}, {"key": "node_3"}]
  }
}
</pre>

Example with manual node/edge parameters: `graph_full_example.json`\
Example with node/edge data mapping: `graph_mapping_example.json`\
Blank Structure Template: `graph_blank_template.json`/


