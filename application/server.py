from flask import Flask, render_template, jsonify
import pendulum
from application import app

pendulum.set_formatter('alternative')


@app.route('/')
def hello_world():
    return render_template('index.html')