// ============================================================
// PATIENT HEALTH MONITORING SYSTEM
// COMPLETE FRONTEND JAVASCRIPT
// ============================================================

let currentPatient = null;


// ============================================================
// ELEMENTS
// ============================================================

const loginPage = document.getElementById("loginPage");
const dashboardPage = document.getElementById("dashboardPage");

const loginForm = document.getElementById("loginForm");
const loginMessage = document.getElementById("loginMessage");

const logoutBtn = document.getElementById("logoutBtn");

const vitalForm = document.getElementById("vitalForm");
const vitalMessage = document.getElementById("vitalMessage");


// ============================================================
// LOGIN
// ============================================================

loginForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
        loginMessage.textContent = "Please enter email and password.";
        loginMessage.style.color = "#c62828";
        return;
    }

    loginMessage.textContent = "Logging in...";
    loginMessage.style.color = "#1976d2";

    try {

        const response = await fetch("/api/login", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        console.log("Login response:", data);

        if (response.ok && data.status === "success") {

            currentPatient = data.patient;

            localStorage.setItem(
                "patient",
                JSON.stringify(currentPatient)
            );

            loginMessage.textContent = "Login successful!";
            loginMessage.style.color = "#2e7d32";

            showDashboard();

        } else {

            loginMessage.textContent =
                data.message || "Invalid email or password.";

            loginMessage.style.color = "#c62828";
        }

    } catch (error) {

        console.error("Login error:", error);

        loginMessage.textContent =
            "Unable to connect to server.";

        loginMessage.style.color = "#c62828";
    }

});


// ============================================================
// SHOW DASHBOARD
// ============================================================

function showDashboard() {

    loginPage.classList.add("hidden");

    dashboardPage.classList.remove("hidden");

    displayPatientInformation();

    loadVitals();
}


// ============================================================
// DISPLAY PATIENT INFORMATION
// ============================================================

function displayPatientInformation() {

    if (!currentPatient) {
        return;
    }

    const patientName =
        document.getElementById("patientName");

    const infoName =
        document.getElementById("infoName");

    const infoAge =
        document.getElementById("infoAge");

    const infoGender =
        document.getElementById("infoGender");

    const infoEmail =
        document.getElementById("infoEmail");

    const infoPhone =
        document.getElementById("infoPhone");


    if (patientName)
        patientName.textContent = currentPatient.name || "-";

    if (infoName)
        infoName.textContent = currentPatient.name || "-";

    if (infoAge)
        infoAge.textContent = currentPatient.age || "-";

    if (infoGender)
        infoGender.textContent = currentPatient.gender || "-";

    if (infoEmail)
        infoEmail.textContent = currentPatient.email || "-";

    if (infoPhone)
        infoPhone.textContent = currentPatient.phone || "-";
}


// ============================================================
// SAVE VITALS
// ============================================================

vitalForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    if (!currentPatient) {

        vitalMessage.textContent =
            "Please login first.";

        vitalMessage.style.color = "#c62828";

        return;
    }


    const bloodPressure =
        document.getElementById("newBloodPressure").value.trim();

    const heartRate =
        document.getElementById("newHeartRate").value;

    const oxygenLevel =
        document.getElementById("newOxygen").value;

    const temperature =
        document.getElementById("newTemperature").value;

    const glucose =
        document.getElementById("newGlucose").value;

    const thyroid =
        document.getElementById("newThyroid").value;


    vitalMessage.textContent = "Saving...";
    vitalMessage.style.color = "#1976d2";


    try {

        const response = await fetch("/api/vitals", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                patient_id: currentPatient.id,

                blood_pressure: bloodPressure,

                heart_rate: heartRate,

                oxygen_level: oxygenLevel,

                temperature: temperature,

                glucose: glucose || null,

                thyroid: thyroid || null

            })

        });


        const data = await response.json();

        console.log("Vital response:", data);


        if (response.ok && data.status === "success") {

            vitalMessage.textContent =
                "Health record saved successfully!";

            vitalMessage.style.color = "#2e7d32";

            vitalForm.reset();

            await loadVitals();

        } else {

            vitalMessage.textContent =
                data.message || "Unable to save record.";

            vitalMessage.style.color = "#c62828";
        }


    } catch (error) {

        console.error("Vital error:", error);

        vitalMessage.textContent =
            "Unable to connect to server.";

        vitalMessage.style.color = "#c62828";
    }

});


// ============================================================
// LOAD VITALS
// ============================================================

async function loadVitals() {

    if (!currentPatient) {
        return;
    }


    try {

        const response = await fetch(
            `/api/vitals/${currentPatient.id}`
        );


        const data = await response.json();

        console.log("Vitals:", data);


        if (!response.ok || data.status !== "success") {

            console.error(
                data.message || "Unable to load vitals."
            );

            return;
        }


        const vitals = data.vitals || [];


        // ----------------------------------------------------
        // LATEST VITAL
        // ----------------------------------------------------

        if (vitals.length > 0) {

            const latest = vitals[0];

            displayLatestVital(latest);

        } else {

            clearLatestVitals();
        }


        // ----------------------------------------------------
        // HISTORY TABLE
        // ----------------------------------------------------

        displayVitalHistory(vitals);


        // ----------------------------------------------------
        // HEALTH STATUS
        // ----------------------------------------------------

        loadHealthStatus();

    } catch (error) {

        console.error("Load vitals error:", error);
    }
}


// ============================================================
// DISPLAY LATEST VITAL
// ============================================================

function displayLatestVital(vital) {

    const bloodPressure =
        document.getElementById("bloodPressure");

    const heartRate =
        document.getElementById("heartRate");

    const oxygenLevel =
        document.getElementById("oxygenLevel");

    const temperature =
        document.getElementById("temperature");

    const glucose =
        document.getElementById("glucose");

    const thyroid =
        document.getElementById("thyroid");


    if (bloodPressure)
        bloodPressure.textContent =
            vital.blood_pressure ?? "--";


    if (heartRate)
        heartRate.textContent =
            vital.heart_rate ?? "--";


    if (oxygenLevel)
        oxygenLevel.textContent =
            vital.oxygen_level ?? "--";


    if (temperature)
        temperature.textContent =
            vital.temperature ?? "--";


    if (glucose)
        glucose.textContent =
            vital.glucose ?? "--";


    if (thyroid)
        thyroid.textContent =
            vital.thyroid ?? "--";
}


// ============================================================
// CLEAR LATEST VITALS
// ============================================================

function clearLatestVitals() {

    document.getElementById("bloodPressure").textContent = "--";

    document.getElementById("heartRate").textContent = "--";

    document.getElementById("oxygenLevel").textContent = "--";

    document.getElementById("temperature").textContent = "--";

    document.getElementById("glucose").textContent = "--";

    document.getElementById("thyroid").textContent = "--";
}


// ============================================================
// DISPLAY VITAL HISTORY
// ============================================================

function displayVitalHistory(vitals) {

    const tableBody =
        document.getElementById("vitalsTableBody");


    if (!tableBody) {
        return;
    }


    tableBody.innerHTML = "";


    if (!vitals || vitals.length === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="7">
                    No health records available
                </td>
            </tr>
        `;

        return;
    }


    vitals.forEach(function (vital) {

        const row = document.createElement("tr");


        row.innerHTML = `

            <td>
                ${vital.created_at || "-"}
            </td>

            <td>
                ${vital.blood_pressure || "-"}
            </td>

            <td>
                ${vital.heart_rate ?? "-"}
            </td>

            <td>
                ${vital.oxygen_level ?? "-"}
            </td>

            <td>
                ${vital.temperature ?? "-"}
            </td>

            <td>
                ${vital.glucose ?? "-"}
            </td>

            <td>
                ${vital.thyroid ?? "-"}
            </td>

        `;


        tableBody.appendChild(row);

    });
}


// ============================================================
// HEALTH STATUS
// ============================================================

async function loadHealthStatus() {

    if (!currentPatient) {
        return;
    }


    const statusElement =
        document.getElementById("healthStatus");


    if (!statusElement) {
        return;
    }


    try {

        const response = await fetch(
            `/api/status/${currentPatient.id}`
        );


        const data = await response.json();


        if (data.status === "success") {

            if (data.health_status === "Normal") {

                statusElement.className =
                    "health-status normal";

                statusElement.textContent =
                    "🟢 " + data.message;

            } else if (data.health_status === "Attention") {

                statusElement.className =
                    "health-status warning";

                statusElement.textContent =
                    "🟡 " + data.message;

            } else {

                statusElement.className =
                    "health-status normal";

                statusElement.textContent =
                    "⚪ " + data.message;
            }

        }

    } catch (error) {

        console.error(
            "Health status error:",
            error
        );
    }
}


// ============================================================
// LOGOUT
// ============================================================

logoutBtn.addEventListener("click", function () {

    currentPatient = null;

    localStorage.removeItem("patient");

    dashboardPage.classList.add("hidden");

    loginPage.classList.remove("hidden");

    document.getElementById("email").value = "";

    document.getElementById("password").value = "";

    loginMessage.textContent = "";

});


// ============================================================
// CHECK PREVIOUS LOGIN
// ============================================================

window.addEventListener("DOMContentLoaded", function () {

    const savedPatient =
        localStorage.getItem("patient");


    if (savedPatient) {

        try {

            currentPatient =
                JSON.parse(savedPatient);

            showDashboard();

        } catch (error) {

            console.error(
                "Saved patient error:",
                error
            );

            localStorage.removeItem("patient");
        }
    }

});