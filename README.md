engine-of-engines
=================

Codebase for Engine of Engines Project

Coffee Compilation
`coffee --compile --watch --output static/js static/coffee`

Sass Compilation
`sass --watch static/scss/:static/css/`

Using Virtual Env
+ Installation
See [this tutorial](http://simononsoftware.com/virtualenv-tutorial/)
+ Freezing virtual env packages
`pip freeze > requirements.txt`
+ Starting virtual env
`source virt_env/venv1/bin/activate`
+ Reloading from requirements.txt (while in virtualenv)
`pip install -r requirements.txt`