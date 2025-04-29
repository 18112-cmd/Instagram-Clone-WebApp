'use strict';

// Import the Firebase libraries (v11.6.1)
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-analytics.js";

//  Your Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDCxDI0RJHL10CggINMGWgYVcuy9VK2TVM",
  authDomain: "instagram-clone-458206.firebaseapp.com",
  projectId: "instagram-clone-458206",
  storageBucket: "instagram-clone-458206.firebasestorage.app",
  messagingSenderId: "813267079244",
  appId: "1:813267079244:web:470cc84ceac4761434e4e9",
  measurementId: "G-H4L1YFCGQV"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const analytics = getAnalytics(app);

// Update UI based on login status
function updateUI(cookie) {
    const token = parseCookieToken(cookie);
  
    const loginBox = document.getElementById("login-box");
    const signOutButton = document.getElementById("sign-out");
  
    if (loginBox && signOutButton) {
      if (token.length > 0) {
        loginBox.hidden = true;
        signOutButton.hidden = false;
      } else {
        loginBox.hidden = false;
        signOutButton.hidden = true;
      }
    }
  }  

// Parse cookie for token
function parseCookieToken(cookie) {
  const strings = cookie.split(';');
  for (let i = 0; i < strings.length; i++) {
    const temp = strings[i].split('=');
    if (temp[0].trim() === "token") {
      return temp[1];
    }
  }
  return "";
}

// Wait until window loads
window.addEventListener("load", function () {
  updateUI(document.cookie);

  // Handle Sign Up
  const signUpBtn = document.getElementById("sign-up");
  if (signUpBtn) {
    signUpBtn.addEventListener("click", function () {
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            const user = userCredential.user;
            user.getIdToken().then((token) => {
            document.cookie = "token=" + token + ";path=/;SameSite=Strict";

            //  New: Call your FastAPI /signup endpoint
            fetch("/signup", {
                method: "POST",
                headers: {
                "Content-Type": "application/json"
                },
                credentials: "include",  // Important to send cookie
                body: JSON.stringify({
                username: document.getElementById("username").value  // take username from input
                })
            })
            .then(response => {
                if (response.ok) {
                console.log("User profile created successfully!");
                window.location = "/timeline";  //  Now redirect
                } else {
                console.error("Failed to create user in Firestore.");
                }
            })
            .catch(error => {
                console.error("Error creating user profile:", error);
            });
            });
        })
        .catch((error) => {
            console.error(error.code + ": " + error.message);
            alert(error.message);
        });
    });
  }

  // Handle Login
  const loginBtn = document.getElementById("login");
  if (loginBtn) {
    loginBtn.addEventListener("click", function () {
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
          const user = userCredential.user;
          console.log("Logged in:", user.email);
          user.getIdToken().then((token) => {
            document.cookie = "token=" + token + ";path=/;SameSite=Strict";
            window.location = "/timeline";
          });
        })
        .catch((error) => {
          console.error(error.code + ": " + error.message);
          alert(error.message);
        });
    });
  }

  // Handle Sign Out
  const signOutBtn = document.getElementById("sign-out");
  if (signOutBtn) {
    signOutBtn.addEventListener("click", function () {
      signOut(auth)
        .then(() => {
          document.cookie = "token=;path=/;SameSite=Strict";
          window.location = "/";
        })
        .catch((error) => {
          console.error(error);
        });
    });
  }
});
