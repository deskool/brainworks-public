const path = require("path");

module.exports = {
    name: "sigma-animate",
    mode: "production",
    entry: "sigma/utils/animate.js",
    output: {
      filename: "sigma_animate.min.js",
      path: path.resolve("app/src/lib"),
      library: {
        name: 'Animate',
        type: 'global'
      },
    }
}
