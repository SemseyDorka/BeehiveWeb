document.addEventListener("DOMContentLoaded", () => {
    
  
    fetch('/kaptarweb/api/meresek') 
        .then(response => response.json())
        .then(adatok => {

          /*
            const xIdovonal = adatok.map(meres => new Date(meres.datum));
            const ySulyok = adatok.map(meres => meres.suly);
*/
            //utolsó 20 mérés
            
               const utolsoMeresek = adatok.slice(-20);
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
                    text: 'Kaptár mérleg adatok alakulása',
                    font: { family: 'Arial, sans-serif', size: 18 }
                },
                xaxis: { 
                    title: 'Dátum',      
                    type: 'date',       
                    gridcolor: '#e5e7eb' 
                },
                yaxis: { 
                    title: 'Súly (kg)',
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