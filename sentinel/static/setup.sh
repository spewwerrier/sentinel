#!/usr/bin/env bash
set -xe

curl -LO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
chmod +x tailwindcss-linux-x64

curl -LO https://github.com/saadeghi/daisyui/releases/latest/download/daisyui.js
curl -LO https://github.com/saadeghi/daisyui/releases/latest/download/daisyui-theme.js


# To compile the css from templates to proper taliwind components you need to run this
# in this folder. And yes IK this can be executed from python web and I don't want to
# complicate the setup process. Automation can be done later
# ./tailwindcss-linux-x64 -i input.css -o output.css --watch
