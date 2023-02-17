from PIL import Image, ImageDraw, ExifTags, ImageColor
import boto3
import json
import io
import os

processed_images_bucket = os.getenv("PROCESSED_IMAGES_BUCKET", default="")

s3_connection = boto3.resource('s3')
s3_client = boto3.client('s3')



def lambda_handler(event, context):
    # Image info
    bucket = event.get('bucket')
    key = event.get('key')
    
    # Gets the image
    s3_object = s3_connection.Object(bucket, key)
    s3_response = s3_object.get()
    
    # Initializes image data
    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)
    imgWidth, imgHeight = image.size
    
    # Initializes Draw object
    draw = ImageDraw.Draw(image)
    object_detected = False
    response = {
        'detected': False
    }
    # Iterates over labels ignoring "non persons"
    for label in event.get('labels'):
        if label.get('name') != 'Person':
            continue
        print("Person found: ", label)
        box = label.get('boundingBox')
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']
        
        points = (
            (left, top),
            (left + width, top),
            (left + width, top+height),
            (left, top + height),
            (left, top)
            )
        draw.line(points, fill='#00d400', width=2)
        # Indicate that a person was found
        object_detected = True
    
    in_mem_file = io.BytesIO()
    image.save(in_mem_file, format=image.format)
    in_mem_file.seek(0)
    
    if(object_detected):
        s3_client.upload_fileobj(in_mem_file, processed_images_bucket, key)
        original_presigned = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key})
        bounded_presigned = s3_client.generate_presigned_url('get_object', Params={'Bucket': processed_images_bucket, 'Key': key})
        print("Original presigned:")
        print(original_presigned)                                              
        response['original_image'] = original_presigned
        response['bounded_image'] = bounded_presigned
        response['detected'] = True
    

    print("Event: ")
    print(event)
    return response
