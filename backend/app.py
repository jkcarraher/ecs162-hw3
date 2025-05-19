import datetime
from flask import Flask, redirect, request, session, jsonify
from flask_cors import CORS 
from pymongo import MongoClient
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
import os
import logging
from bson.objectid import ObjectId



app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.urandom(24)

oauth = OAuth(app)

nonce = generate_token()


oauth.register(
    name=os.getenv('OIDC_CLIENT_NAME'),
    client_id=os.getenv('OIDC_CLIENT_ID'),
    client_secret=os.getenv('OIDC_CLIENT_SECRET'),
    #server_metadata_url='http://dex:5556/.well-known/openid-configuration',
    authorization_endpoint="http://localhost:5556/auth",
    token_endpoint="http://dex:5556/token",
    jwks_uri="http://dex:5556/keys",
    userinfo_endpoint="http://dex:5556/userinfo",
    device_authorization_endpoint="http://dex:5556/device/code",
    client_kwargs={'scope': 'openid email profile'}
)

# Setup MongoDB client (adjust this as needed)
client = MongoClient(os.getenv('MONGO_URI'))
db = client.nyt_comments_db  # your database name
comments_collection = db.comments

@app.route('/')
def home():
    return redirect('http://localhost:5173')

@app.route('/login')
def login():
    session['nonce'] = nonce
    redirect_uri = 'http://localhost:8000/authorize'
    return oauth.flask_app.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/authorize')
def authorize():
    token = oauth.flask_app.authorize_access_token()
    nonce = session.get('nonce')

    user_info = oauth.flask_app.parse_id_token(token, nonce=nonce)  # or use .get('userinfo').json()
    session['user'] = user_info
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)


@app.route('/api/key')
def get_key():
    return jsonify({'apiKey': os.getenv('NYT_API_KEY')})

@app.route('/api/user')
def get_user():
    user = session.get('user')
    if user:
        is_moderator = "moderator" in user.get("name", "").lower()
        user["isModerator"] = is_moderator
        return jsonify(user)
    return jsonify({'error': 'No user logged in'}), 401

@app.route('/api/comment', methods=['POST'])
def post_comment():
    user = session.get('user')
    if not user:
        return jsonify({'error': 'User not logged in'}), 401

    data = request.get_json()

    # Expected payload: articleId, commentText and an optional parentCommentId
    article_id = data.get("articleId")
    comment_text = data.get("commentText")
    parent_comment_id = data.get("parentCommentId")
        
    if not article_id or not comment_text:
        return jsonify({'error': 'Missing required fields'}), 400

    # Build the comment document. If parent_comment_id is provided, this is treated as a reply.
    comment = {
        "articleId": article_id,
        "parentCommentId": parent_comment_id,  # can be None if it's a top-level comment
        "commentText": comment_text,
        "user": user,  # store the whole user object or just part of it (e.g., user['email'])
        "createdAt": datetime.datetime.utcnow()
    }
    result = comments_collection.insert_one(comment)
    comment['_id'] = str(result.inserted_id)
    return jsonify(comment), 201

@app.route('/api/comments/<article_id>', methods=['GET'])
def get_article_comments(article_id):
    logging.debug(f"Checking existing comments with id: ", article_id)
    comments_cursor = comments_collection.find({"articleId": article_id})
    logging.debug(f"Cursor ", comments_cursor)
    comments = []
    logging.debug(f"Comments", comments)
    for comment in comments_cursor:
        comment['_id'] = str(comment['_id'])
        if isinstance(comment.get("createdAt"), datetime.datetime):
            comment["createdAt"] = comment["createdAt"].isoformat()
        comments.append(comment)
    return jsonify(comments)

def get_descendant_ids(parent_id: str) -> list:
    descendants = []
    children = comments_collection.find({"parentCommentId": parent_id})
    for child in children:
        child_id = str(child["_id"])
        descendants.append(child_id)
        descendants.extend(get_descendant_ids(child_id))
    return descendants

@app.route('/api/comment/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    # Require the user to be logged in
    user = session.get('user')
    if not user:
        return jsonify({'error': 'User not logged in'}), 401

    # Fetch the comment from the database
    try:
        comment = comments_collection.find_one({"_id": ObjectId(comment_id)})
    except Exception as e:
        return jsonify({"error": "Invalid comment ID"}), 400

    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    # Check if the user is allowed to delete this comment.
    comment_owner_email = comment.get("user", {}).get("email")
    logged_in_email = user.get("email")
    is_moderator = "moderator" in user.get("name", "").lower()

    if comment_owner_email != logged_in_email and not is_moderator:
        return jsonify({"error": "Not authorized to delete this comment"}), 403

    # Get all descendant comment IDs recursively
    descendant_ids = get_descendant_ids(comment_id)
    all_ids = [ObjectId(comment_id)] + [ObjectId(child_id) for child_id in descendant_ids]

    # Delete the parent comment and all its descendants
    try:
        result = comments_collection.delete_many({"_id": {"$in": all_ids}})
        if result.deleted_count > 0:
            return jsonify({"message": "Comment and its child comments deleted successfully"}), 200
        else:
            return jsonify({"error": "Comment not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400