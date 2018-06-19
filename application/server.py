from flask import Flask, render_template, jsonify
from application.solar_analytics_scraper import SessionData, SITE_IDS
import pendulum
from application import app, s

pendulum.set_formatter('alternative')


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/data/<site_id>')
def data(site_id=36929):
    today_date = pendulum.now().format('YYYYMMDD')
    site_data = s.fetch_detailed_site_data(site_id, today_date, today_date)
    site_status = s.site_status(site_id)['data'] if 'data' in s.site_status(site_id) else False
    site_details = s.site_details(site_id)
    weather = s.get_weather(site_id)
    daily_data = s.daily_data(site_id, today_date, today_date)['data'][0]
    print (daily_data)
    time_step = site_data['t_step']
    output = []
    total_generation = 0
    for d in site_data['data']:
        time = pendulum.parse(d['t_stamp'])
        energy_generated = d['energy_generated'] if d['energy_generated'] else 0
        total_generation += energy_generated
        power_generated = energy_generated / time_step
        energy_consumed = d['energy_consumed'] if d['energy_consumed'] else 0
        power_consumed = energy_consumed / time_step
        output.append([time.int_timestamp * 1000, power_generated, power_consumed])
    print (site_id, ': ', total_generation)
    return jsonify({
        'solar': output,
        'status': site_status,
        'daily': daily_data,
        'details': site_details,
        'weather': weather
    })


# app.run(debug=True)
