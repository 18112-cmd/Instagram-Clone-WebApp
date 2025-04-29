from google.cloud import firestore
from datetime import datetime
from typing import List, Dict

# Initialize Firestore client
db = firestore.Client()

# Define Firestore Collections
USER_COLLECTION = 'User'
POST_COLLECTION = 'Post'

### --------------- USER FUNCTIONS --------------- ###

def create_user_if_not_exists(user_id: str, username: str):
    """Create a new user document if it doesn't already exist."""
    user_ref = db.collection(USER_COLLECTION).document(user_id)
    if not user_ref.get().exists:
        user_ref.set({
            'username': username,
            'followers': [],
            'following': [],
            'created_at': datetime.utcnow()
        })

def follow_user(current_user_id: str, target_user_id: str):
    """Follow another user."""
    current_user_ref = db.collection(USER_COLLECTION).document(current_user_id)
    target_user_ref = db.collection(USER_COLLECTION).document(target_user_id)

    current_user_ref.update({
        'following': firestore.ArrayUnion([target_user_id])
    })
    target_user_ref.update({
        'followers': firestore.ArrayUnion([current_user_id])
    })

def unfollow_user(current_user_id: str, target_user_id: str):
    """Unfollow another user."""
    current_user_ref = db.collection(USER_COLLECTION).document(current_user_id)
    target_user_ref = db.collection(USER_COLLECTION).document(target_user_id)

    current_user_ref.update({
        'following': firestore.ArrayRemove([target_user_id])
    })
    target_user_ref.update({
        'followers': firestore.ArrayRemove([current_user_id])
    })

def get_followers(user_id: str) -> List[str]:
    """Get list of followers for a user."""
    user_doc = db.collection(USER_COLLECTION).document(user_id).get()
    if user_doc.exists:
        return user_doc.to_dict().get('followers', [])
    return []

def get_following(user_id: str) -> List[str]:
    """Get list of users the user is following."""
    user_doc = db.collection(USER_COLLECTION).document(user_id).get()
    if user_doc.exists:
        return user_doc.to_dict().get('following', [])
    return []

### --------------- POST FUNCTIONS --------------- ###

def create_post(username: str, image_url: str, caption: str):
    post_ref = db.collection('Post').document()
    post_ref.set({
        'Username': username,
        'Date': datetime.utcnow(),
        'image_url': image_url,
        'caption': caption,
    })


def get_user_posts(user_id: str) -> List[Dict]:
    """Get posts for a single user ordered by Date descending."""
    
    #  Fetch username first
    user_doc = db.collection(USER_COLLECTION).document(user_id).get()
    if not user_doc.exists:
        return []

    username = user_doc.to_dict().get('username', 'anonymous')

    #  Now query posts by Username (not user_id)
    posts = db.collection(POST_COLLECTION)\
        .where('Username', '==', username)\
        .order_by('Date', direction=firestore.Query.DESCENDING)\
        .stream()
        
    return [post.to_dict() for post in posts]

def get_timeline_posts(user_id: str) -> List[Dict]:
    """Get 50 recent posts from the user and the people they follow."""
    user_doc = db.collection(USER_COLLECTION).document(user_id).get()
    if not user_doc.exists:
        return []

    user_data = user_doc.to_dict()
    following_ids = user_data.get('following', [])  # List of user IDs (document IDs)

    # Fetch usernames for following users
    usernames = []

    for fid in following_ids:
        fdoc = db.collection(USER_COLLECTION).document(fid).get()
        if fdoc.exists:
            fdata = fdoc.to_dict()
            usernames.append(fdata.get('username'))

    # Also add current user's own username
    usernames.append(user_data.get('username'))

    # Firestore 'in' query limit is 10
    if len(usernames) > 10:
        usernames = usernames[:10]

    posts_query = db.collection(POST_COLLECTION)\
        .where('Username', 'in', usernames)\
        .order_by('Date', direction=firestore.Query.DESCENDING)\
        .limit(50)\
        .stream()

    return [post.to_dict() for post in posts_query]


### --------------- COMMENT FUNCTIONS --------------- ###

def add_comment(post_id: str, username: str, comment: str):
    """Add a comment to a post (limit 200 characters)."""
    if len(comment) > 200:
        raise ValueError("Comment exceeds 200 characters limit.")

    comment_ref = db.collection(POST_COLLECTION).document(post_id).collection('Comments').document()
    comment_ref.set({
        'username': username,
        'comment': comment,
        'date': datetime.utcnow()
    })

def get_comments(post_id: str, limit: int = 5) -> List[Dict]:
    """Get comments for a post ordered by date descending."""
    comments = db.collection(POST_COLLECTION).document(post_id).collection('Comments')\
                .order_by('date', direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
    return [comment.to_dict() for comment in comments]

def get_all_comments(post_id: str) -> List[Dict]:
    """Get all comments for a post."""
    comments = db.collection(POST_COLLECTION).document(post_id).collection('Comments')\
                .order_by('date', direction=firestore.Query.DESCENDING)\
                .stream()
    return [comment.to_dict() for comment in comments]

def get_username_by_user_id(user_id: str) -> str:
    """Fetch the username from Firestore given a user_id."""
    user_doc = db.collection('User').document(user_id).get()
    if user_doc.exists:
        return user_doc.to_dict().get('username', 'anonymous')
    return 'anonymous'