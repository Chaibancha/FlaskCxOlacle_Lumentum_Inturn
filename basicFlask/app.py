from flask import Flask, send_file, render_template, json, request, redirect, Response,url_for, jsonify, session
import cx_Oracle

app = Flask(__name__)

@app.route('/')
def index():
    data = {"name":"chaibancha", "age":30, "salary":"30000"}
    return render_template('index.html', mydata = data)

@app.route('/about')
def about():
    product = ["t-shirt", "pan", "Technology"]
    return render_template('about.html', myproduct = product)

@app.route('/admin')
def profile():
    username = "chaibancha"
    return render_template('admin.html', username = username)


if __name__ == '__main__':
    app.run(debug=True)
