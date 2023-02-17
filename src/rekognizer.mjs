// Import required AWS SDK clients and commands for Node.js
import { DetectLabelsCommand } from  "@aws-sdk/client-rekognition";
import  { RekognitionClient } from "@aws-sdk/client-rekognition";

// Set the AWS Region.
//const REGION = "region-name"; //e.g. "us-east-1"
// Create SNS service object.
const rekogClient = new RekognitionClient();

const bucket = 'bucket-name'
const photo = 'photo-name'



const detect_labels = async (params) => {
    try {
        const response = await rekogClient.send(new DetectLabelsCommand(params));
        console.log(response.Labels)
        const labels = response.Labels.map(l => {
            return {
                name: l.Name,
                boundingBox: l.Instances[0]?.BoundingBox
            }
        })
        return labels; // For unit tests.
      } catch (err) {
        console.log("Error", err);
      }
};

export const handler = async(event) => {
    const bucket = event['detail']['bucket']['name']
    const key = event['detail']['object']['key']
    
    // Set params
    const params = {
        Image: {
          S3Object: {
            Bucket: bucket,
            Name: key
          },
        },
      }
      
    const labels = await detect_labels(params);
      
    return {
        bucket,
        key,
        labels
    }
};

