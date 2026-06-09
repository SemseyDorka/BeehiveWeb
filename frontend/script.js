document.addEventListener("DOMContentLoaded", async () => {
    const tablaTorzs = document.getElementById("meresek-torzs");

    try {
        const response = await fetch('/api/meresek');
        if (!response.ok) throw new Error("Hiba történt az adatok lekérésekor.");

        const adatok = await response.json();
        tablaTorzs.innerHTML = "";

        if (adatok.length === 0) {
            tablaTorzs.innerHTML = `<tr><td colspan="4" class="text-center text-warning">Nincsenek adatok.</td></tr>`;
            return;
        }
        //első 20 sor 
        i=0
        adatok.forEach(meres => {
            if (i<=20)
            {
                            const sor = document.createElement("tr");
            sor.innerHTML = `
                <td>${meres.id}</td>
                <td>${new Date(meres.datum).toLocaleString('hu-HU')}</td>
                <td>${meres.suly} kg</td>
                <td>${meres.homerseklet} °C</td>
            `;
            tablaTorzs.appendChild(sor);

            }
            
        });
    } catch (error) {
        console.error(error);
        tablaTorzs.innerHTML = `<tr><td colspan="4" class="text-center text-danger">A szerver nem elérhető!</td></tr>`;
    }
});