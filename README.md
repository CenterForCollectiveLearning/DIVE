engine-of-engines
=================

Codebase for Engine of Engines Project

Coffee Compilation
-----------------
coffee --compile --watch --output static/js static/coffee

Sass Compilation
-----------------
sass --watch static/scss/:static/css/

Using Virtual Env
-----------------
# Installation
See [this tutorial](http://simononsoftware.com/virtualenv-tutorial/)
# Freezing virtual env packages
`pip freeze > requirements.txt`
# Reloading from requirements.txt
`virtualenv --no-site-packages --distribute .env && source .env/bin/activate && pip install -r requirements.txt`