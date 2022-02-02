const path = require("path");

module.exports = {
    name: "sigma",
    mode: "production",
    entry: "sigma/build/sigma.js",
    output: {
      filename: "sigma.min.js",
      path: path.resolve("app/src/lib"),
      library: {
        type: "global",
        name: "sigma"
      }
    }
}
