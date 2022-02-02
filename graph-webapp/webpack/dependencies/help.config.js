const path = require("path");

module.exports = {
    name: "help",
    mode: "production",
    entry: "./app/src/help.js",
    output: {
      filename: "help.min.js",
      path: path.resolve("app/static/js")
    }
}
