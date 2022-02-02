const path = require("path");

module.exports = {
    name: "visualization",
    mode: "production",
    entry: "./app/src/graph.js",
    output: {
      filename: "graph.min.js",
      path: path.resolve("app/static/js")
    }
}
