const path = require("path");

module.exports = {
    name: "graphology-shortest_path",
    mode: "production",
    entry: "graphology-shortest-path/unweighted.js",
    output: {
      filename: "shortest_path.min.js",
      path: path.resolve("app/src/lib"),
      library: {
        name: 'shortestPath',
        type: 'global'
      },
    }
}
