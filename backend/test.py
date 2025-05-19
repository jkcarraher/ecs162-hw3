import unittest
from unittest.mock import patch, MagicMock
from app import app as flask_app
import datetime
import json
import os

class AppTestCase(unittest.TestCase):
    def setUp(self):
        flask_app.config['TESTING'] = True
        self.app = flask_app.test_client()

    # API key fetch correctly
    @patch.dict(os.environ, {'NYT_API_KEY': 'test-api-key'})
    def test_get_key(self):
        response = self.app.get('/api/key')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'apiKey': 'test-api-key'})

    # Admin test
    def test_logged_in_admin(self):
        with self.app.session_transaction() as session:
            session['user'] = {
                'name': 'admin',
                'email': 'admin@hw3.com'
            }
        
        response = self.app.get('api/user')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data['name'], 'admin')
        self.assertEqual(data['email'], 'admin@hw3.com')
        self.assertTrue(data['isModerator'])

    # Mod test
    def test_logged_in_moderator(self):
        with self.app.session_transaction() as session:
            session['user'] = {
                'name': 'moderator',
                'email': 'moderator@hw3.com'
            }
        
        response = self.app.get('api/user')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data['name'], 'moderator')
        self.assertEqual(data['email'], 'moderator@hw3.com')
        self.assertTrue(data['isModerator'])

    # User test
    def test_logged_in_user(self):
        with self.app.session_transaction() as session:
            session['user'] = {
                'name': 'user',
                'email': 'user@hw3.com'
            }
        
        response = self.app.get('api/user')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data['name'], 'user')
        self.assertEqual(data['email'], 'user@hw3.com')
        self.assertFalse(data['isModerator'])

    # Not logged in
    def test_not_logged_in(self):
        response = self.app.get('/api/user')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()['error'], 'No user logged in')

    @patch('app.comments_collection.insert_one')
    def test_comment_success(self, mock_insert_one):
        mock_insert_one.return_value.inserted_id = '42'

        with self.app.session_transaction() as session:
            session['user'] = {
                'name': 'user',
                'email': 'user@hw3.com'
            }
        
        comment = {
            'articleId': 'thisIsArticleId',
            'commentText': 'POG Champ!',
            'parentCommentId': None
        }

        response = self.app.post('/api/comment', json=comment)
        self.assertEqual(response.status_code, 201)

        data = response.get_json()
        self.assertEqual(data['_id'], '42')
        self.assertEqual(data['articleId'], 'thisIsArticleId')
        self.assertEqual(data['commentText'], 'POG Champ!')
        self.assertEqual(data['parentCommentId'], None)

    @patch('app.comments_collection.find')
    def test_article_comments(self, mock_find):
        mock_find.return_value = [
            {
                '_id': '42',
                'articleId': 'thisIsArticleId',
                'commentText': 'POG Champ!',
                'createdAt': datetime.datetime(2025, 5, 18),
                'user': {'name': 'user'}
            }
        ]

        res = self.app.get('/api/comments/thisIsArticleId')
        self.assertEqual(res.status_code, 200)
        
        data = res.get_json()
        self.assertEqual(len(data), 1) # Only one comment posted
        self.assertEqual(data[0]['articleId'], 'thisIsArticleId')

if __name__ == '__main__':
    unittest.main()