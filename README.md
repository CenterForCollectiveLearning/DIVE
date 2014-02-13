engine-of-engines
=================

Codebase for Engine of Engines Project

Using Virtual Env
-----------------
# Installation
See [this tutorial](http://simononsoftware.com/virtualenv-tutorial/)
# Freezing virtual env packages
`pip freeze > requirements.txt`
# Reloading from requirements.txt
`virtualenv --no-site-packages --distribute .env && source .env/bin/activate && pip install -r requirements.txt`