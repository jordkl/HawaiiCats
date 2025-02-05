import os
from firebase_admin import storage
import uuid
from dotenv import load_dotenv

class FirebaseStorageManager:
    def __init__(self):
        try:
            # Load environment variables
            load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env.local'))
            
            # Get bucket name from environment or use default
            bucket_name = os.getenv('FIREBASE_STORAGE_BUCKET', 'catmap-e5581.appspot.com')
            print(f"DEBUG: Using storage bucket: {bucket_name}")
            
            # Explicitly specify the bucket name
            self.bucket = storage.bucket(bucket_name)
            if not self.bucket:
                raise ValueError("Could not get storage bucket")
            print(f"Successfully initialized storage bucket: {self.bucket.name}")
            
            # List contents of the bucket for debugging
            print(f"DEBUG: Listing contents of bucket {bucket_name}:")
            try:
                blobs = list(self.bucket.list_blobs(prefix='sighting_photos/'))
                for blob in blobs:
                    print(f"Found file: {blob.name}")
            except Exception as e:
                print(f"Error listing bucket contents: {e}")
                
        except Exception as e:
            print(f"Error initializing storage bucket: {str(e)}")
            raise

    def upload_image(self, file_data, content_type=None):
        """
        Upload an image to Firebase Storage in the sighting_photos folder
        
        Args:
            file_data: The file data to upload
            content_type: The content type of the file (e.g., 'image/jpeg')
            
        Returns:
            dict: A dictionary containing the public URL and filename
        """
        try:
            if not self.bucket:
                raise ValueError("Storage bucket not initialized")

            # Generate a unique filename with original extension
            original_filename = file_data.filename
            file_extension = os.path.splitext(original_filename)[1] if original_filename else '.jpg'
            unique_filename = f"sighting_photos/{str(uuid.uuid4())}{file_extension}"
            
            print(f"Creating blob for {unique_filename}")
            # Create a new blob and upload the file data
            blob = self.bucket.blob(unique_filename)
            
            # Reset the file pointer to the beginning
            file_data.seek(0)
            
            # Set the content type if provided
            if content_type:
                blob.content_type = content_type
                
            print(f"Uploading file...")
            # Upload the file
            blob.upload_from_file(file_data, content_type=content_type)
            
            print(f"Making file public...")
            # Make the file publicly accessible
            blob.make_public()
            
            print(f"Successfully uploaded file to {unique_filename}")
            return {
                'url': blob.public_url,
                'filename': unique_filename
            }
            
        except Exception as e:
            print(f"Error uploading file to Firebase Storage: {str(e)}")
            raise

# Global instance
_storage_manager = None

def init_storage_manager():
    """Initialize the global storage manager instance"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = FirebaseStorageManager()
    return _storage_manager

def get_storage_manager():
    """Get the global storage manager instance"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = FirebaseStorageManager()
    return _storage_manager
