from google.cloud import storage
import uuid

# Initialize Storage client
storage_client = storage.Client()

# Reference your storage bucket
BUCKET_NAME = "instagram-clone-458206.firebasestorage.app"
bucket = storage_client.bucket(BUCKET_NAME)

def upload_image(file_data, content_type: str) -> str:
    """
    Upload an image file to Cloud Storage and return its public URL.
    Only accepts 'image/png' or 'image/jpeg' content types.
    """

    if content_type not in ['image/png', 'image/jpeg']:
        raise ValueError("Invalid file type. Only PNG and JPG allowed.")

    # Generate a unique filename
    file_id = str(uuid.uuid4())
    extension = "png" if content_type == "image/png" else "jpg"
    blob = bucket.blob(f"uploads/{file_id}.{extension}")

    # Upload file
    blob.upload_from_string(file_data, content_type=content_type)

    # Make the file publicly accessible
    blob.make_public()

    # Return public URL
    return blob.public_url
