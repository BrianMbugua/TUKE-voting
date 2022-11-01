
import face_recognition
import cv2
import numpy as np
from tukevoting.models import VoterFaces
from flask_login import current_user
from tukevoting import db
from tukevoting.models import Voter, VoterFaces
from flask import flash

def run_face_rec():

    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(1)

    # Load a sample picture and learn how to recognize it.
    brian_image = face_recognition.load_image_file("tukevoting/images/brian-mbugua/1.jpg")
    brian_face_encoding = face_recognition.face_encodings(brian_image)[0]

    # Load a second sample picture and learn how to recognize it.
    emilia_image = face_recognition.load_image_file("tukevoting/images/voter1/2.jpg")
    emilia_face_encoding = face_recognition.face_encodings(emilia_image)[0]

    yusuf_image = face_recognition.load_image_file("tukevoting/images/voter3/1.png")
    yusuf_face_encoding = face_recognition.face_encodings(yusuf_image)[0]

     
    amal_image = face_recognition.load_image_file("tukevoting/images/amal_faruk/1.jpg")
    amal_face_encoding = face_recognition.face_encodings(amal_image)[0]

    # Create arrays of known face encodings and their names
    known_face_encodings = [
        brian_face_encoding,
        emilia_face_encoding,
        yusuf_face_encoding,
        amal_face_encoding
    ]
    known_face_names = [
        "Brian Mbugua",
        "Emilia Clarke",
        "Yusuf Kamau",
        "Amal Faruk"
    ]
    known_roll_num = [
        565565,
        165164,
        654648,
        566292
    ]

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    face_nums = []
    process_this_frame = True

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Only process every other frame of video to save time
        if process_this_frame:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            face_nums = []
            
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                        
                    
                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    rollnum = known_roll_num[best_match_index]


                face_names.append(name)
                face_nums.append(rollnum)
            
                

        process_this_frame = not process_this_frame

        

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            cv2.putText(frame, "PRESS Y WHEN DONE TO EXIT", (50, 50), font, 1.0, (255, 255, 255), 1)


        # Display the resulting image 
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('y'):
            break

        
    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

    if matches[best_match_index]:
        if current_user.roll_num == known_roll_num[best_match_index]:
            allow_to_vote = VoterFaces(roll_num=current_user.roll_num, allow_vote=True)
            db.session.add(allow_to_vote)
            db.session.commit()
        else:
            flash("Not your face", 'danger')

    
    
    
     