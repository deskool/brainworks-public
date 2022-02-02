const path = require("path");

module.exports = {
    name: "graphology",
    mode: "production",
    entry: "graphology/dist/graphology.esm.js",
    output: {
      filename: "graphology.min.js",
      path: path.resolve("app/src/lib"),
      library: {
        type: "global",
        name: "graphology"
      }
    }
}
