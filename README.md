Data Integration and Visualization Engine (DIVE)
=================================================
The Data Integration and Visualization Engine (DIVE) is a platform for semi-automatically generating web-based, interactive visualizations of structured data sets. Data visualization is a useful method for understanding complex phenomena, communicating information, and informing inquiry. However, available tools for data visualization are difficult to learn and use, require a priori knowledge of what visualizations to create. See [dive.media.mit.edu](http://dive.media.mit.edu) for more information.

Write-up and documentation
---------
See this [Google Doc](https://docs.google.com/document/d/1J_wwbELz9l_KOoB6xRpUASH1eAzaZpHSRQvMJ_4sJgI/edit?usp=sharing).

Development task list
---------
See our [Trello](https://trello.com/b/yKWRcTqT). Currently private, PM Kevin for access.

Development Build Process
---------
1. Run `npm install` in base directory to get development and client-side dependencies.
2. In one terminal session, `gulp` in base directory (if gulp is installed globally) else `./node_modules/.bin/gulp` to build `./dist` directory and run development server. Access server at localhost:3000 in browser.
3. In another terminal session, run API (see below, default port 8888).

Deployment Build Process
---------
1. Run `gulp build` to build `./dist` directory

Using Virtual Env to Manage Server-Side Dependencies
---------
0. Install [Homebrew](http://brew.sh/) if you don't already have it.
1. Installation: See [this fine tutorial](http://simononsoftware.com/virtualenv-tutorial/).
2. Freezing virtual env packages: `pip freeze > requirements.txt`.
3. Starting virtual env: `source venv/bin/activate`.
4. Reloading from `requirements.txt` (while virtualenv is active): `pip install -r requirements.txt`.
4. Install XQuartz: `brew install Caskroom/cask/xquartz`.
5. Install Cairo: `brew install cairo`.
6. Install MongoDB: `brew install mongodb` and follow the instructions to run mongodb on login and immediately.

Run Server-Side Code / API
---------
1. Load virtual environment.
2. In active virtual environment with all dependencies, run Flask server: `python ./server/run.py`.
