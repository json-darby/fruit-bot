from inference_sdk import InferenceHTTPClient
import matplotlib.pyplot as plt
from PIL import Image
import io

'''Performs multi-object detection on fruit images using Roboflow and draws bounding boxes.'''

def predict_and_draw(image_path):
    '''
    Connects to Roboflow API to detect multiple fruit objects in an image.
    Draws bounding boxes and confidence scores on the image, then saves the result.
    '''
    CLIENT = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key="dtPOWUN60iGi0OxQ1nkZ"
    )
    result = CLIENT.infer(image_path, model_id="fruit-dataset-comp5544/4")
    # print("Roboflow Inference Response:", result)
    
    img = Image.open(image_path)
    fig, ax = plt.subplots()
    ax.imshow(img)
    
    predictions = result.get("predictions", [])
    for pred in predictions:
        x_center = pred['x']
        y_center = pred['y']
        width = pred['width']
        height = pred['height']
        
        top_left_x = x_center - width / 2
        top_left_y = y_center - height / 2
        
        rect = plt.Rectangle((top_left_x, top_left_y), width, height,
                             edgecolor='red', facecolor='none', linewidth=2)
        ax.add_patch(rect)
        
        label = f"{pred['class']} ({pred['confidence'] * 100:.1f}%)"
        ax.text(top_left_x, top_left_y, label, fontsize=10, color='yellow',
                bbox=dict(facecolor='red', alpha=0.5))
    
    plt.axis('off')
    plt.savefig("fruit_prediction.png", format="png", bbox_inches="tight")
    plt.show()
    plt.close(fig)
    return "fruit_prediction.png"

# output_file = predict_and_draw("C:/Users/I_NEE/Desktop/New folder/66995ec7f19c6f66d24b3948_shutterstock_439030861.jpg")
# print("Saved prediction as:", output_file)

# img = Image.open("fruit_prediction.png")
# img.show()

