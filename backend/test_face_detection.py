from coloranalysis.ai.face_detection import FaceDetectionService

service = FaceDetectionService()
result = service.detect_face("1.jpeg")  # schimbă cu poza ta

print(result)