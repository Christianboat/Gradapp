import os
import unittest
from app import create_app, db
from app.models import User, Application, Task, Document
from config import Config
import io
from datetime import datetime, timedelta

class TestAdvancedFeatures(unittest.TestCase):
    def setUp(self):
        # Use an in-memory database for testing
        class TestConfig(Config):
            TESTING = True
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            WTF_CSRF_ENABLED = False
            UPLOAD_FOLDER = 'tests/test_uploads'

        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        db.create_all()
        
        # Create Dummy User
        self.user = User(username='tester', email='test@example.com')
        self.user.set_password('password')
        db.session.add(self.user)
        db.session.commit()
        
        # Create Dummy Application
        self.application = Application(
            title='Test App', 
            institution='Test Uni', 
            application_type='Job',
            deadline=datetime.utcnow() + timedelta(days=30),
            user_id=self.user.id
        )
        db.session.add(self.application)
        db.session.commit()
        
        # Ensure upload dir exists
        if not os.path.exists('tests/test_uploads'):
            os.makedirs('tests/test_uploads')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        # Clean up uploads
        import shutil
        import time
        if os.path.exists('tests/test_uploads'):
            try:
                shutil.rmtree('tests/test_uploads', ignore_errors=True)
            except Exception as e:
                print(f"Cleanup warning: {e}")

    def login(self):
        return self.client.post('/auth/login', data=dict(
            email='test@example.com',
            password='password'
        ), follow_redirects=True)

    def test_task_management(self):
        self.login()
        
        # 1. Add Task
        response = self.client.post(f'/applications/{self.application.id}/add_task', data={
            'description': 'Submit Transcripts'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        task = Task.query.first()
        self.assertIsNotNone(task)
        self.assertEqual(task.description, 'Submit Transcripts')
        print("[OK] Task Creation: Success")

        # 2. Toggle Task
        response = self.client.post(f'/applications/task/{task.id}/toggle')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(task.is_completed)
        print("[OK] Task Toggling: Success")

        # 3. Delete Task
        response = self.client.post(f'/applications/task/{task.id}/delete')
        self.assertEqual(response.status_code, 200)
        count = Task.query.count()
        self.assertEqual(count, 0)
        print("[OK] Task Deletion: Success")

    def test_document_management(self):
        self.login()
        
        # 1. Upload Document
        data = {
            'file': (io.BytesIO(b"dummy content"), 'test.txt')
        }
        response = self.client.post(
            f'/applications/{self.application.id}/upload_document', 
            data=data, 
            content_type='multipart/form-data',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        doc = Document.query.first()
        self.assertIsNotNone(doc)
        self.assertEqual(doc.filename, 'test.txt')
        print("[OK] Document Upload: Success")
        
        # 2. Delete Document
        response = self.client.post(f'/applications/document/{doc.id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        count = Document.query.count()
        self.assertEqual(count, 0)
        print("[OK] Document Deletion: Success")

if __name__ == '__main__':
    unittest.main()
