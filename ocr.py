# from PIL import Image
# import pytesseract
# import numpy as np

# filename = 'a.jpeg'
# img1 = np.array(Image.open(filename))
# text = pytesseract.image_to_string(img1)
# print(text)

import Vision
import Cocoa
from Foundation import NSURL

# Load image from file
image_url = NSURL.fileURLWithPath_("a.jpeg")
handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(image_url, None)

# Setup OCR request
def handle(request, error):
    results = request.results()
    for observation in results:
        candidates = observation.topCandidates_(1)
        if candidates:
            print(candidates[0].string())

request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handle)
request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)

# Perform OCR
handler.performRequests_error_([request], None)
