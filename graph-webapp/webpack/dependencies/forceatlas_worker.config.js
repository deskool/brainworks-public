const path = require("path");

module.exports = {
    name: "graphology-forceatlas2-worker",
    mode: "production",
    entry: "graphology-layout-forceatlas2/worker.js",
    output: {
      filename: "forceatlas2_worker.min.js",
      path: path.resolve("app/src/lib"),
      library: {
        name: 'FA2Layout',
        type: 'global'
      },
    }
}
