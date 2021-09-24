import tempfile

from PIL import Image
from core.users.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class TestImageView(APITestCase):
    def test_file_is_accepted(self):
        admin = User.objects.create_user(username='admin',
                                         email='admin@admin.com',
                                         password='1234qwerasdf',
                                         is_staff=True,
                                         is_superuser=True)
        self.client.force_login(admin)
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        tmp_file.seek(0)
        response = self.client.post('http://localhost:8000/api/images/1/post/',
                                    {'image': tmp_file},
                                    format='multipart')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
