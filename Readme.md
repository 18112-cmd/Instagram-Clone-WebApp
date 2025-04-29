# 📸 Instagram Clone – FastAPI + Firebase

This project is a minimal Instagram-like web application implemented using **FastAPI** as the backend, **Firebase Authentication** for user login/logout, **Firestore** for database operations, and **Google Cloud Storage** for media storage. It supports user registration, posting images with captions, following/unfollowing users, viewing timelines, and a basic comment system.

---

## 🔍 Purpose

The goal of this project is to demonstrate the development of a scalable, cloud-integrated web app using modern backend and frontend tools. The application replicates core social media features and showcases the integration of Firebase and Google Cloud with FastAPI.

---

## 🛠 Technologies Used

- **FastAPI** – Backend RESTful API framework  
- **Firebase Authentication** – User login and session management  
- **Firestore** – NoSQL document-based database for user and post data  
- **Google Cloud Storage** – Upload and serve image files  
- **HTML + Bootstrap** – Frontend user interface  
- **JavaScript** – Firebase SDK logic

---

## ✨ Features Implemented

### ✅ Group 1 – Core Functionality
- User login and logout with Firebase Authentication
- Firestore collections: `User` and `Post` with required fields
- Initialize user profile on first login
- Composite index created for Post: `Username (asc)`, `Date (desc)`

### ✅ Group 2 – Profile & Post
- User profile page displaying own posts (latest first)
- Create new post: image upload + caption
- Follower and Following counts redirect to their respective lists

### ✅ Group 3 – Social Features
- Timeline with 50 most recent posts from self and followed users
- Search by username prefix and view other users' profiles
- Follow/Unfollow users from their profile pages

### ✅ Group 4 – Comment System
- Add comments (max 200 characters)
- Display top 5 comments under each post
- Expand button to show full comment list

---

## ⚙️ Run Locally

1. Install dependencies  
   `pip install -r requirements.txt`

2. Set up `.env` or environment variables for GCP credentials i.e. run this in terminal $env:GOOGLE_APPLICATION_CREDENTIALS="path to this file\instagram-clone-458206-3ae649e7ae64.json"

3. Run the app  
   `uvicorn main:app --reload`

---


## 📚 References

- [Firebase Authentication Documentation](https://firebase.google.com/docs/auth)
- [Google Cloud Firestore Documentation](https://cloud.google.com/firestore/docs)
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
