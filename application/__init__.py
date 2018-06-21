from flask import Flask, render_template, jsonify
import pendulum

pendulum.set_formatter('alternative')
app = Flask(__name__)

from application import server