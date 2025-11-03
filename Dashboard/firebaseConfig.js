// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCc8PCc1IYikEQXJ4_5avlOJM9JqIrH7Ac",
  authDomain: "backbeacon.firebaseapp.com",
  databaseURL: "https://backbeacon-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "backbeacon",
  storageBucket: "backbeacon.firebasestorage.app",
  messagingSenderId: "287132718497",
  appId: "1:287132718497:web:99e72324a1ca257f1627e0"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const database = firebase.database();
