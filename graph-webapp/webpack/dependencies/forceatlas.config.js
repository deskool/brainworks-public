const path = require("path");

module.exports = {
    name: "graphology-forceatlas2",
    mode: "production",
    entry: "graphology-layout-forceatlas2/index.js",
    output: {
      filename: "forceatlas2.min.js",
      path: path.resolve("app/src/lib"),
      library: {
        name: 'FA2',
        type: 'global'
      },
    }
}
