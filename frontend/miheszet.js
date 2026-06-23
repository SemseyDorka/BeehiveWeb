
let mediaRecorder;
let audioChunks = [];
let streamRef = null; 

const micBtn = document.getElementById('micBtn');
const micStatus = document.getElementById('micStatus');
const naploSzoveg = document.getElementById('naploSzoveg');

micBtn.addEventListener('click', async () => {

    if (!mediaRecorder || mediaRecorder.state === "inactive") {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamRef = stream; 
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
            
          
            mediaRecorder.onstop = async () => {
                micStatus.innerText = " Hang feldolgozása ...";
                micBtn.disabled = true; 
                
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                
                const formData = new FormData();
                formData.append('audio', audioBlob, 'memo.wav');

                try {
                    const res = await fetch('/api/transcribe', { 
                        method: 'POST', 
                        body: formData 
                    });

                    if (!res.ok) {
                        const errorData = await res.json().catch(() => ({ detail: "Ismeretlen szerverhiba történt." }));
                        throw new Error(errorData.detail || "Szerveroldali hiba.");
                    }

                    const data = await res.json();
                    if (data.text) {
                        naploSzoveg.value = (naploSzoveg.value ? " " : "") + data.text;
                        micStatus.innerText = " ";
                    }
                } catch (err) {
                    micStatus.innerText = ` Hiba: ${err.message}`;
                    console.error("Whisper API hiba:", err);
                } finally {
                    micBtn.disabled = false;
                    micBtn.innerHTML = " Beszéd indítása";
                    micBtn.classList.replace('btn-danger', 'btn-outline-danger');
                    
                    if (streamRef) {
                        streamRef.getTracks().forEach(track => track.stop());
                    }
                }
            };

            mediaRecorder.start();
            micBtn.innerHTML = "Megállítás";
            micBtn.classList.replace('btn-outline-danger', 'btn-danger'); 
            micStatus.innerText = " Rögzítés folyamatban...";

        } catch (err) {
            micStatus.innerText = " Nem sikerült hozzáférni a mikrofonhoz. Engedélyezd a böngészőben!";
            console.error(err);
        }
    } 
    else {
        mediaRecorder.stop();
    }
});

//elemzés llama-3.1-8b-instant 
document.getElementById('elemzesBtn').addEventListener('click', async () => {
    const text = naploSzoveg.value.trim();
    if (!text) {
        alert("Írj valamit vagy használd a hangrögzítőt!");
        return;
    }

    const spinner = document.getElementById('loadingSpinner');
    const eredmenyDiv = document.getElementById('elemzesEredmeny');
    
    spinner.classList.remove('d-none');

    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const data = await res.json();

        spinner.classList.add('d-none');
        if (data.analysis) {
            console.log(data.analysis)
            eredmenyDiv.innerText = data.analysis;
            naploSzoveg.value = ""; 
        } else {
            alert("Hiba: " + data.error);
        }
    } catch (err) {
        spinner.classList.add('d-none');
    }
});