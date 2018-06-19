from flask import Flask, render_template, jsonify
from application.solar_analytics_scraper import SessionData, SITE_IDS
import pendulum

pendulum.set_formatter('alternative')
app = Flask(__name__)
app_2 = Flask(__name__)

s = SessionData()
s.login()

from application import server