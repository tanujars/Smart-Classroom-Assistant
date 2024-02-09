import boto3
import os
from boto3 import client as boto3_client
import face_recognition
import pickle
from math import e
from boto3.dynamodb.conditions import Key

# AWS credentials and configuration
aws_access_key = xyz
aws_secret_access_key = abc
storage_path = "/tmp/"
input_bucket_name = 'inputbucket-lasnubes'
output_bucket_name = 'outputbucket-lasnubes'

# Function to read the 'encoding' file
def open_encoding(filename):
    file = open(filename, "rb")
    data = pickle.load(file)
    file.close()
    return data

def face_recognition_handler(event, context):
    # Establish AWS session and resource connections
    session = boto3.Session(aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_access_key, region_name='us-east-1')
    dynamo_resource = session.resource('dynamodb')
    dynamo_table = dynamo_resource.Table('Student_data')
    s3 = boto3_client('s3', region_name='us-east-1', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_access_key)

    # Retrieve list of objects from input S3 bucket
    list_objects = s3.list_objects_v2(Bucket=input_bucket_name)

    # Download and load the known face data from the 'encoding' file
    s3.download_file(input_bucket_name, 'encoding', storage_path + 'encoding')
    known_data = open_encoding(storage_path + 'encoding')
    known_names = known_data['name']
    known_encodings = known_data['encoding']

    try:
        # Iterate through the objects in the input bucket
        for item in list_objects["Contents"]:
            key = item["Key"]
            if key != "encoding":
                # Download and process video file to extract face images
                video_file = key
                s3.download_file(input_bucket_name, video_file, storage_path + key)
                s3.delete_object(Bucket=input_bucket_name, Key=key)
                video_file = storage_path + key
                os.system("ffmpeg -i " + str(video_file) + " -r 1 " + str(storage_path) + "image-%3d.jpeg")

                # Load the first extracted face image
                image_file = storage_path + "image-001.jpeg"
                image = face_recognition.load_image_file(image_file)

                # Find face locations and encodings in the image
                face_locations = face_recognition.face_locations(image)
                face_encodings = face_recognition.face_encodings(image, face_locations)

                names = []
                # Compare face encodings with known encodings
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_encodings, face_encoding)
                    first_match_index = next((i for i, match in enumerate(matches) if match), None)
                    if first_match_index is not None:
                        name = known_names[first_match_index]
                        names.append(name)

                # Query DynamoDB for additional student information based on the recognized face
                response = dynamo_table.query(
                    KeyConditionExpression=Key('name').eq(names[0])
                )
                items = response['Items']
                for item in items:
                    # Prepare output data
                    output_data = key + ',' + item['name'] + ',' + item['major'] + ',' + item['year']
                    # Upload output data to the output S3 bucket
                    s3.put_object(Bucket=output_bucket_name, Key=key.split('.')[0] + ".csv", Body=output_data)
                    print(output_data)
    except Exception as e:
        print("Error:", e)
