// script.js

// Reference the Realtime Database path
const dataRef = database.ref("backbeacon");

// Listen for changes in the database
dataRef.limitToLast(1).on("child_added", (snapshot) => {
  const data = snapshot.val();

  document.getElementById("seatStatus").textContent = data.seat_status || "N/A";
  document.getElementById("posture").textContent = data.posture || "N/A";
  document.getElementById("distance").textContent = data.distance ?? "N/A";
  document.getElementById("timestamp").textContent = data.timestamp || "N/A";
});
