#!/bin/bash
export API_URL=http://127.0.0.1:8000
cd workspaces/server
volta run --node 20.11.1 node ./dist/server.js