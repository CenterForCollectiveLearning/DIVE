Data Integration and Visualization Engine (DIVE)
=================================================
The Data Integration and Visualization Engine (DIVE) is a platform for semi-automatically generating web-based, interactive visualizations of structured data sets. Data visualization is a useful method for understanding complex phenomena, communicating information, and informing inquiry. However, available tools for data visualization are difficult to learn and use, require a priori knowledge of what visualizations to create.

Write-up, vision, and documentation
---------
See [Google Doc](https://docs.google.com/document/d/1J_wwbELz9l_KOoB6xRpUASH1eAzaZpHSRQvMJ_4sJgI/edit?usp=sharing)

Development Build Process
---------
1. Run 'npm install' to get development and client-side dependencies
2. Run 'gulp' (if gulp install globally) else ./node_modules/.bin/gulp to build ./dist directory and run development server

Deployment Build Process
---------
1. Run 'gulp build' to build ./dist directory

Using Virtual Env to Manage Server-Side Dependencies
---------
1. Installation
See [this tutorial](http://simononsoftware.com/virtualenv-tutorial/)
2. Freezing virtual env packages
`pip freeze > requirements.txt`
3. Starting virtual env
`source virt_env/venv1/bin/activate`
4. Reloading from requirements.txt (while in virtualenv)
`pip install -r requirements.txt`

Run Server-Side Code / API
---------
1. Load virtual environment
2. Run Flask server
`python ./server/run.py`
