/* ------------------------------------------------------------
   BackBeacon Dashboard - Real-Time Monitoring Script
-------------------------------------------------------------*/
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getDatabase, ref, onValue, push } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-database.js";
import { firebaseConfig } from "./firebase-config.js";

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const database = getDatabase(app);
const backBeaconRef = ref(database, 'BackBeacon');

// DOM elements
const statusElem = document.getElementById("status");
const distanceElem = document.getElementById("distance");
const timestampElem = document.getElementById("timestamp");

// Real-time listener
onValue(backBeaconRef, (snapshot) => {
  const data = snapshot.val();
  if (data) {
    const { status, distance_cm, timestamp } = data;
    statusElem.textContent = `Status: ${status}`;
    distanceElem.textContent = `Distance: ${distance_cm} cm`;
    timestampElem.textContent = `Last Updated: ${timestamp}`;

    statusElem.style.color = status === "SLOUCH DETECTED" ? "red" :
                             status === "GOOD POSTURE" ? "green" : "gray";
  } else {
    statusElem.textContent = "No data available.";
    distanceElem.textContent = "";
    timestampElem.textContent = "";
  }
});

// Optional function to send data manually (for testing)
export function sendPostureData(status, distance) {
  const timestamp = new Date().toISOString();
  push(backBeaconRef, { status, distance_cm: distance, timestamp });
}
