from flask import Flask, render_template, redirect, url_for
# from flask.ext.scss import Scss
# from flask_cake import Cake

app = Flask(__name__, static_path='/static')
# cake = Cake()
# cake.init_app(app)
# Scss(app)

@app.route('/')
def main():
    return render_template('/main.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')