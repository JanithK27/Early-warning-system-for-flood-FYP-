async function predictFlood() {
    let discharge = document.getElementById("discharge").value;
    let rainfall = document.getElementById("rainfall").value;
    let waterlevel = document.getElementById("waterlevel").value;

    if (discharge && rainfall && waterlevel) { // Ensure all inputs are filled
        let data = {
            discharge_rate: parseFloat(discharge),
            rainfall: parseFloat(rainfall),
            water_level: parseFloat(waterlevel)
        };

        try {
            let response = await fetch("http://127.0.0.1:5000/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            let result = await response.json();

            // Display predictions
            document.getElementById("hour1").innerText = result["Next 1 Hour Water Level"].toFixed(2) + " m";
            document.getElementById("hour2").innerText = result["Next 2 Hours Water Level"].toFixed(2) + " m";
            document.getElementById("hour3").innerText = result["Next 3 Hours Water Level"].toFixed(2) + " m";

            // Display alert messages
            document.getElementById("alert1").innerText = result["Alert 1"];
            document.getElementById("alert2").innerText = result["Alert 2"];
            document.getElementById("alert3").innerText = result["Alert 3"];

        } catch (error) {
            console.error("Error:", error);
        }
    }
}

// Add event listeners to trigger prediction automatically when input fields are filled
document.getElementById("discharge").addEventListener("input", predictFlood);
document.getElementById("rainfall").addEventListener("input", predictFlood);
document.getElementById("waterlevel").addEventListener("input", predictFlood);
