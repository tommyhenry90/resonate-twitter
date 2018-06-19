import requests
import json
from datetime import datetime
from calendar import monthrange
# from pandas.io.json import json_normalize
# import pandas as pd
# import pendulum
# from flask import Flask

SITE_DICT = {
    36929: 'RCR Swan Hill', 
    28514: 'Robertson', 
    28856: "Stephen Donnelly's Property", 
    28513: 'Robertson', 
    25128: 'Mittagong Quarry Genset Load', 
    34378: 'Loombah', 
    140: 'Jarnason Alexandria', 
    35150: 'Yarradale Stud', 
    7567: '5B Workshop', 
    7568: 'Appin Main - R1000', 
    35400: 'Mittagong Grid Connected', 
    25656: "8 Bill O'Reilly Close", 
    5499: 'Mittagong Quarry 1', 
    37596: 'Beverford - Solar Rentals', 
    25213: 'Cedarvale Farm', 
    28735: 'The Finch House'
}

SITE_LOCATIONS = {
    36929: (-35.3453212, 143.5230547),
    28856: (-32.7361274, 151.2962636),
    28513: (-34.5867492,150.6336753),
    35150: (-31.77257, 116.13771),
    35400: (-34.3995434441, 150.329759348),
    37596: (-35.2053609, 143.4458829)
}


class Site:
    def __init__(self, site_id, site_name, lat, lon):
        self.id = site_id
        self.name = site_name
        self.lat = lat
        self.lon = lon


SITE_IDS = [36929, 28514, 28856, 28513, 25128, 34378, 140, 35150, 7567, 7568, 35400, 25656, 5499, 37596, 25213, 28735]


class SessionData:
    def __init__(self):
        self.session = requests.session()

    def login(self, url="https://my.solaranalytics.com/au/", usr="tommy.henry@5b.com.au", pwd="5Billion5"):
        # Open login page
        self.login_raw = self.session.get(url)
        login_text = self.login_raw.text
        token_index = login_text.find('csrf')
        csrf_token_string = login_text[token_index+8:]
        csfr_end = csrf_token_string.find("'")
        self.csrf_token = str(csrf_token_string[:csfr_end])
        # add inputs to payload
        self.payload = {
            "email": usr,
            "password": pwd,
            "remember_me": "on",
            "csrfmiddlewaretoken": self.csrf_token,
            "next": "/au/login/"
        }
        # append login url for post
        request_url = url
        # post information and login
        result = self.session.post(
            request_url,
            data=self.payload
        )
        print (result)
        result_text = result.text
        basic_index = result_text.find('Basic')
        basic_string = result.text[basic_index:]
        basic_end = basic_string.find("'")
        self.session.headers["Authorization"] = str(basic_string[:basic_end])
        return result

    def fetch_status(self, system_id='25656'):
        url = "https://portal.solaranalytics.com.au/api/v2/site_status/" + system_id
        result = self.session.get(
            url
        )
        # print today_data
        data = json.loads(result.text)
        return data

    def fetch_site_performance(self, site_id, t_end, t_start):
        url = 'https://portal.solaranalytics.com.au/api/v2/site_data/' + str(site_id) + '?tend=' + str(t_end) + '&tstart=' + str(t_start)
        result = self.session.get(
            url,
        )
        data = json.loads(result.text)
        print (data)
        return data["data"]

    def fetch_detailed_site_data(self, site_id, t_end, t_start):
        url = 'https://portal.solaranalytics.com.au/api/v2/site_data/' + str(site_id) + '?gran=minute&losses=false&tend=' + str(t_end) + '&tstart=' + str(t_start)
        result = self.session.get(
            url,
        )
        data = json.loads(result.text)
        return data

    def fetch_site_list(self):
        url = "https://portal.solaranalytics.com.au/api/v3/site_list?address=true&capacity=true&hardware=true&id=true&notes=true&state=true&subscription=true"
        result = self.session.get(url)
        data = json.loads(result.text)["data"]
        site_ids = {}
        for site in data:
            site_name = str(site["s_cli_site_name"])
            site_id = site["site_id"]
            site_ids[site_id] = site_name
        return site_ids

    def monthly_summary(self, site_id, month = datetime.now().strftime("%m"), year = datetime.now().strftime("%Y")):
        month_str = str(month)
        year_str = str(year)
        t_start = year_str + month_str + "01"
        t_end = year_str + month_str + str(monthrange(int(year), int(month))[1])
        # print t_start, t_end
        result = self.fetch_site_performance(str(site_id), str(t_end), str(t_start))
        return result

    def get_weather(self, site_id):
        lat, lon = SITE_LOCATIONS[int(site_id)]
        url = 'https://my.solaranalytics.com/weather/?lat=' + str(lat) + '&lon=' + str(lon)
        old_accept = self.session.headers["Accept"]
        self.session.headers["Accept"] = "application/json, text/plain, */*"
        result = self.session.get(
            url
        )
        self.session.headers["Accept"] = old_accept
        data = json.loads(result.text)
        return data

    def get_super_detailed_data(self):
        url = 'https://portal.solaranalytics.com.au/api/v2/device_data?all=true&device=D704206249039&tstart=2018-02-22'
        result = self.session.get(
            url
        )
        data = result.text
        return data

    def summarise_all_sites(self, month = datetime.now().strftime("%m"), year = datetime.now().strftime("%Y")):
        file_name = str(year) + str(month) + ".xlsx"
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
        summary = {}
        for site_id in SITE_IDS:
            site_data = self.monthly_summary(site_id, month, year)["data"]
            ms = json_normalize(site_data)
            ms["performance"] = ms["energy_generated"] / ms["energy_expected"]
            ms["generation_percentage"] = ms["energy_generated"] / ms["energy_consumed"]
            sheet_name = str(site_id)
            ms.to_excel(writer, sheet_name)
            summary[site_id] = ms
        performance_summary = {}
        for site_id in summary:
            # find totals for each site
            total_energy_consumed = summary[site_id]["energy_consumed"].sum()
            total_energy_expected = summary[site_id]["energy_expected"].sum()
            total_energy_generated = summary[site_id]["energy_generated"].sum()
            if total_energy_expected:
                performance = total_energy_generated / total_energy_expected
            else:
                performance = None
            if total_energy_consumed:
                generation_percentage = total_energy_generated / total_energy_consumed
            else:
                generation_percentage = None
            site_name = SITE_DICT[site_id]
            # insert information into summary table
            performance_summary[site_id] = {
                "site_name": site_name,
                "total_energy_consumed": total_energy_consumed,
                "total_energy_expected": total_energy_expected,
                "total_energy_generated": total_energy_generated,
                "performance": performance,
                "generation_percentage": generation_percentage
            }
        df = pd.DataFrame(performance_summary).transpose()
        df.to_excel(writer, sheet_name="performance_summary", columns=["site_name", "total_energy_consumed",
                                                                       "total_energy_expected", "total_energy_generated",
                                                                       "performance", "generation_percentage"])

        # Get the xlsxwriter workbook and worksheet objects.
        workbook  = writer.book
        worksheet = writer.sheets['performance_summary']

        # Add some cell formats.
        format1 = workbook.add_format({'num_format': '#,##0.00'})
        format2 = workbook.add_format({'num_format': '0%'})

        # Light red fill with dark red text.
        bad_format = workbook.add_format({'bg_color':   '#FFC7CE',
                                       'font_color': '#9C0006'})

        # Light yellow fill with dark yellow text.
        ok_format = workbook.add_format({'bg_color':   '#FFEB9C',
                                       'font_color': '#9C6500'})

        # Green fill with dark green text.
        good_format = workbook.add_format({'bg_color':   '#C6EFCE',
                                       'font_color': '#006100'})

        # Note: It isn't possible to format any cells that already have a format such
        # as the index or headers or any cells that contain dates or datetimes.

        # Set the column width and format.
        worksheet.set_column('F:G', 18, format2)

        # Set the format but not the column width.
        worksheet.set_column('C:E', None, format1)

        worksheet.conditional_format('F2:F17', {'type':     'cell',
                                        'criteria': '>=',
                                        'value':    0.95,
                                        'format':   good_format})
        worksheet.conditional_format('F2:F17', {'type':     'cell',
                                        'criteria': '>=',
                                        'value':    0.9,
                                        'format':   ok_format})
        worksheet.conditional_format('F2:F17', {'type':     'cell',
                                        'criteria': '<',
                                        'value':    0.9,
                                        'format':   bad_format})
        writer.save()
        return df

    def date_range_summary(self, site_id, t_end, t_start):
        file_name = SITE_DICT[site_id] + " " + str(t_start) + " to " + str(t_end) + ".xlsx"
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
        site_data = self.fetch_site_performance(site_id, t_end, t_start)
        ms = json_normalize(site_data)
        sheet_name = str(t_start) + " to " + str(t_end)
        ms.to_excel(writer, sheet_name)
        writer.save()
        return ms

    def savings_lookup(self, site_id, t_end, t_start):
        url = "https://portal.solaranalytics.com.au/api/v3/site_savings/" + str(site_id) + \
              "?by_date=true&gran=total&end_date=" + str(t_end) + "&start_date=" + str(t_start)
        result = self.session.get(
            url
        )
        data = json.loads(result.text)
        return data

    def import_export_lookup(self, site_id, t_end, t_start):
        url = "https://portal.solaranalytics.com.au/api/v2/export_site_sum_data/" + str(site_id) + \
              "?end_date=" + str(t_end) + "&start_date=" + str(t_start)
        result = self.session.get(
            url
        )
        data = json.loads(result.text)
        return data

    def site_details(self, site_id):
        url = "https://portal.solaranalytics.com.au/api/v1/site_details/" + str(site_id) + "?site=true"
        result = self.session.get(
            url
        )
        data = json.loads(result.text)
        return data

    def site_status(self, site_id):
        url = "https://portal.solaranalytics.com.au/api/v4/site_status/" + str(site_id)
        result = self.session.get(
            url
        )
        data = json.loads(result.text)
        return data

    def daily_data(self, site_id, t_start, t_end):
        url = "https://portal.solaranalytics.com.au/api/v2/site_data/" + str(site_id) + "?gran=day&losses=true&tend=" + str(t_end) + "&tstart=" + str(t_start)
        result = self.session.get(
            url
        )
        data = json.loads(result.text)
        return data


class DataAnalysis:
    def __init__(self, site_id):
        self.site_id = site_id

    def parse_data(self, data):
        pass


def main():
    s = SessionData()
    s.login()
    site_id = 28513
    print (s.site_status(site_id))


if __name__ == '__main__':
    main()