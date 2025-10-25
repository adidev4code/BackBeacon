/* ------------------------------------------------------------
   BackBeacon Dashboard - Real-Time Monitoring Script
   ------------------------------------------------------------
   - Fetches posture data from Firebase Realtime Database
   - Updates webpage with posture status and distance
   - Uses color and text to show user's posture feedback
------------------------------------------------------------- */

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getDatabase, ref, onValue } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-database.js";
import { firebaseConfig } from "./firebase-config.js";

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const database = getDatabase(app);
const backBeaconRef = ref(database, 'BackBeacon');

// DOM elements
const statusElem = document.getElementById("status");
const distanceElem = document.getElementById("distance");
const timestampElem = document.getElementById("timestamp");

// Realtime data listener
onValue(backBeaconRef, (snapshot) => {
  const data = snapshot.val();
  if (data) {
    const { status, distance_cm, timestamp } = data;

    statusElem.textContent = `Status: ${status}`;
    distanceElem.textContent = `Distance: ${distance_cm} cm`;
    timestampElem.textContent = `Last Updated: ${timestamp}`;

    if (status === "SLOUCH DETECTED") {
      statusElem.style.color = "red";
    } else if (status === "GOOD POSTURE") {
      statusElem.style.color = "green";
    } else {
      statusElem.style.color = "gray";
    }
  } else {
    statusElem.textContent = "No data available.";
  }
});
