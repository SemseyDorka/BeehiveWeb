document.addEventListener("DOMContentLoaded", () => {


    fetch('/kaptarweb/api/meresek')
        .then(response => response.json())
        .then(adatok => {

            /*
              const xIdovonal = adatok.map(meres => new Date(meres.datum));
              const ySulyok = adatok.map(meres => meres.suly);
  */
            //utolsó 20 mérés

            const utolsoMeresek = adatok.slice(0, 20);
            const xIdovonal = utolsoMeresek.map(meres => new Date(meres.datum));
            const ySulyok = utolsoMeresek.map(meres => meres.suly);


            const trace = {
                x: xIdovonal,
                y: ySulyok,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Súly (kg)',
                line: {
                    color: '#4f46e5',
                    width: 3
                },
                marker: {
                    size: 6,
                    color: '#4f46e5'
                }
            };


            const layout = {
                title: {
                    font: { family: 'Arial, sans-serif', size: 12 }
                },
                xaxis: {
                    title: 'Dátum',
                    type: 'date',
                    fixedrange: true,
                    gridcolor: '#e5e7eb'
                },
                yaxis: {
                    title: 'Súly (kg)',
                    fixedrange: true,
                    gridcolor: '#e5e7eb'
                },
                margin: { t: 50, b: 50, l: 60, r: 30 },
                paper_bgcolor: '#ffffff',
                plot_bgcolor: '#f8fafc'
            };

            const config = {
                responsive: true,
                displaylogo: false
            };

            Plotly.newPlot('plotly-chart', [trace], layout, config);
        })
        .catch(error => {
            console.error("Hiba történt a grafikon adatainak letöltésekor:", error);
            document.getElementById('plotly-chart').innerHTML =
                `<div class="alert alert-danger m-3">Nem sikerült betölteni a grafikont .</div>`;
        });


});
//felhasználó által  variálható "dashboard"

document.addEventListener("DOMContentLoaded", () => {

    fetch('/kaptarweb/api/meresek')
        .then(response => response.json())
        .then(adatok => {


            const x_date = adatok.map(meres => new Date(meres.datum));
            const y_weight = adatok.map(meres => meres.suly);


            var trace1 = {
                type: "scatter",
                mode: "lines",
                name: 'AAPL High',
                x: x_date,
                y: y_weight,
                line: { color: '#4f46e5' }
            }


            var data = [trace1];

            var layout = {
                title: { text: 'Kaptársúly változása' },
                xaxis: {
                    autorange: true,
                    range: ['2015-02-17', '2017-02-16'],
                    rangeselector: {
                        buttons: [
                            {
                                count: 24,
                                label: '24 óra',
                                step: 'hour',
                                stepmode: 'backward'
                            },
                            {
                                count: 7,
                                label: '1 hét',
                                step: 'day',
                                stepmode: 'backward'
                            },
                            {
                                count: 1,
                                label: '1 hónap',
                                step: 'month',
                                stepmode: 'backward'
                            },
                            {
                                count: 6,
                                label: '6 hónap',
                                step: 'month',
                                stepmode: 'backward'
                            },
                            {
                                step: 'all',
                                label: 'Összes mérés'
                            }
                        ]
                    },
                    type: 'date'
                },
                yaxis: {
                    fixedrange:true,
                    autorange: true,
                    range: [86.8700008333, 138.870004167],
                    type: 'linear',
                    title: 'Súly (kg)'
                }

            };
            const config = {
                responsive: true,
                displaylogo: false
            };

            Plotly.newPlot('plotly-dashboard-chart', data, layout);
        })
});