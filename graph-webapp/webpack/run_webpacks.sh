#!/usr/bin/env bash

# Run webpack for each config file in the dependencies directory
for file in webpack/dependencies/*.config.js; do
    npx webpack --config $file
done

### now pack up the whole thing for production
npx webpack --config webpack/production.config.js

echo Webpack Completed.

