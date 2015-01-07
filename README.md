Data Integration and Visualization Engine (DIVE)
=================================================

# Build Process
1. Run 'npm install'
2. Run 'gulp' (if gulp install globally) else ./node_modules/.bin/gulp

# Using Virtual Env
+ Installation
See [this tutorial](http://simononsoftware.com/virtualenv-tutorial/)
+ Freezing virtual env packages
`pip freeze > requirements.txt`
+ Starting virtual env
`source virt_env/venv1/bin/activate`
+ Reloading from requirements.txt (while in virtualenv)
`pip install -r requirements.txt`