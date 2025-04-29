from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from services.firestore_service import get_username_by_user_id
from fastapi.staticfiles import StaticFiles
import requests
from typing import Optional
import os
from google.cloud import firestore

from services.firestore_service import (
    create_user_if_not_exists, follow_user, unfollow_user,
    get_user_posts, get_followers, get_following,
    create_post, get_timeline_posts, add_comment, get_comments, get_all_comments
)
from services.storage_service import upload_image

from models.user_model import UserCreate, FollowAction
from models.post_model import PostCreate, CommentCreate

# Initialize FastAPI app
app = FastAPI()

db = firestore.Client()


# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Firebase project configuration
FIREBASE_API_KEY = "AIzaSyDCxDI0RJHL10CggINMGWgYVcuy9VK2TVM" 

# Dependency: Verify Firebase ID Token manually (no firebase-admin)
def verify_token(request: Request):
    token = request.cookies.get('token')
    if not token:
        raise HTTPException(status_code=401, detail="No auth token provided.")

    firebase_verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "idToken": token
    }

    response = requests.post(firebase_verify_url, headers=headers, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")

    decoded_token = response.json()['users'][0]  # Extract user info
    return decoded_token

# -----------------------------------------------
# ROUTES
# -----------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/timeline", response_class=HTMLResponse)
async def timeline_page(request: Request):
    return templates.TemplateResponse("timeline.html", {"request": request})

@app.get("/create-post", response_class=HTMLResponse)
async def create_post_page(request: Request):
    return templates.TemplateResponse("post.html", {"request": request})

@app.get("/search-users", response_class=HTMLResponse)
async def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

# -----------------------------------------------
# API ENDPOINTS
# -----------------------------------------------

# Create User on first login
@app.post("/signup")
async def signup(user: UserCreate, decoded_token=Depends(verify_token)):
    user_id = decoded_token["localId"]  # Now using 'localId' instead of 'uid'
    create_user_if_not_exists(user_id, user.username)
    return {"message": "User created successfully."}

# Get current user's profile
@app.get("/api/profile", response_class=JSONResponse)
async def get_profile(decoded_token=Depends(verify_token)):
    user_id = decoded_token["localId"]

    username = get_username_by_user_id(user_id)  #  Fetch username from Firestore safely

    followers = get_followers(user_id)
    following = get_following(user_id)
    posts = get_user_posts(user_id)

    return {
        "username": username,
        "followers": followers,
        "following": following,
        "posts": posts
    }

# Follow another user
@app.post("/follow")
async def follow(action: FollowAction, decoded_token=Depends(verify_token)):
    user_id = decoded_token["localId"]
    follow_user(user_id, action.target_user_id)
    return {"message": "Followed successfully."}

# Unfollow another user
@app.post("/unfollow")
async def unfollow(action: FollowAction, decoded_token=Depends(verify_token)):
    user_id = decoded_token["localId"]
    unfollow_user(user_id, action.target_user_id)
    return {"message": "Unfollowed successfully."}

# Upload a new post
@app.post("/create-post")
async def create_new_post(request: Request, file: UploadFile = File(...), caption: str = Form(...), decoded_token=Depends(verify_token)):
    user_id = decoded_token["localId"]

    username = get_username_by_user_id(user_id) 

    contents = await file.read()
    public_url = upload_image(contents, file.content_type)

    create_post(username, public_url, caption)

    return {"message": "Post created successfully."}


# Fetch user's timeline
@app.get("/api/timeline", response_class=JSONResponse)
async def get_timeline(decoded_token=Depends(verify_token)):
    user_id = decoded_token["localId"]
    posts = get_timeline_posts(user_id)
    return posts

# Add a comment to a post
from services.firestore_service import get_username_by_user_id

@app.post("/add-comment")
async def add_new_comment(comment: CommentCreate, decoded_token=Depends(verify_token)):
    user_id = decoded_token["localId"]

    #  Correctly fetch username from Firestore
    username = get_username_by_user_id(user_id)

    add_comment(comment.post_id, username, comment.comment)
    return {"message": "Comment added successfully."}

# Get limited comments (top 5 by default)
@app.get("/comments/{post_id}", response_class=JSONResponse)
async def fetch_comments(post_id: str, limit: Optional[int] = 5):
    comments = get_comments(post_id, limit)
    return comments

# Search users by username (starting match)
@app.get("/search", response_class=JSONResponse)
async def search_users(query: str, decoded_token=Depends(verify_token)):
    from google.cloud import firestore
    db = firestore.Client()
    users = db.collection('User').stream()
    results = []

    for user in users:
        user_data = user.to_dict()
        if user_data['username'].lower().startswith(query.lower()):
            results.append({
                "id": user.id,
                "username": user_data['username']
            })

    return results

@app.get("/followers", response_class=HTMLResponse)
async def followers_page(request: Request):
    return templates.TemplateResponse("followers.html", {"request": request})

@app.get("/following", response_class=HTMLResponse)
async def following_page(request: Request):
    return templates.TemplateResponse("following.html", {"request": request})


@app.get("/api/followers", response_class=JSONResponse)
async def api_get_followers(decoded_token=Depends(verify_token)):
    user_id = decoded_token["localId"]
    follower_ids = get_followers(user_id)

    result = []
    for fid in follower_ids:
        username = get_username_by_user_id(fid)
        result.append({"id": fid, "username": username})

    #  Reverse order
    result = result[::-1]
    return result

@app.get("/api/following", response_class=JSONResponse)
async def api_get_following(decoded_token=Depends(verify_token)):
    user_id = decoded_token["localId"]
    following_ids = get_following(user_id)

    result = []
    for fid in following_ids:
        username = get_username_by_user_id(fid)
        result.append({"id": fid, "username": username})

    #  Reverse order
    result = result[::-1]
    return result

@app.get("/api/user/{user_id}", response_class=JSONResponse)
async def api_get_user_profile(user_id: str, decoded_token=Depends(verify_token)):
    # Fetch user info
    user_doc = db.collection('User').document(user_id).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_doc.to_dict()
    username = user_data.get('username', 'anonymous')

    # Check if current user is following
    current_user_id = decoded_token["localId"]
    current_user_doc = db.collection('User').document(current_user_id).get()
    current_following = current_user_doc.to_dict().get('following', [])

    is_following = user_id in current_following

    # Fetch posts for that user
    posts = db.collection('Post')\
        .where('Username', '==', username)\
        .order_by('Date', direction=firestore.Query.DESCENDING)\
        .limit(50)\
        .stream()

    posts_data = [post.to_dict() for post in posts]

    return {
        "username": username,
        "posts": posts_data,
        "is_following": is_following
    }


@app.get("/user/{user_id}", response_class=HTMLResponse)
async def view_other_profile(request: Request, user_id: str):
    return templates.TemplateResponse("other_profile.html", {"request": request, "user_id": user_id})
