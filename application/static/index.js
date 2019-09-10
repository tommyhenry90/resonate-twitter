google.charts.load('current', {
    'packages': ['geochart'],
    // Note: you will need to get a mapsApiKey for your project.
    // See: https://developers.google.com/chart/interactive/docs/basic_load_libs#load-settings
    'mapsApiKey': 'AIzaSyD-9tSrke72PouQMnMX-a7eZSW0jkFMBWY'
});

google.charts.setOnLoadCallback(drawRegionsMap);

function drawRegionsMap() {
    var data = google.visualization.arrayToDataTable([
        ['Country', 'Greenness'],
        ['Australia', 200]
    ]);

    var options = {'height': 694, 'width': 1112, magnifyingGlass:{enable: true, zoomFactor: 7.5}}

    var chart = new google.visualization.GeoChart(document.getElementById('regions_div'));

    chart.draw(data, options);
}


google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

function drawChart() {
    var data = google.visualization.arrayToDataTable([
        ['Energy Type', 'kWh'],
        ['Combustibles', data.combustibles],
        ['Geothermal', data.geothermal],
        ['Hydro', data.hydro],
        ['Nuclear', data.nuclear],
        ['Solar', data.solar],
        ['Wind', data.wind],
        ['Other', data.other]
    ]);

    var options = {
        title: 'Energy Mix'
    };

    var chart = new google.visualization.PieChart(document.getElementById('piechart'));
chart.draw(data, options);
}