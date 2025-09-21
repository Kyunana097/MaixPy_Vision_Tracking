'''
    Face recognize demo, download modle from maixhub first:
            https://maixhub.com/
'''

from maix import nn, display, camera, image
from maix.nn.app import face
from maix.nn.app.face import FaceRecognize
import time
from evdev import InputDevice
from select import select


def get_keys(device):
    '''
        @return is_left_pressed, is_right_pressed
    '''
    left = False
    right = False
    r,w,x = select([device], [], [], 0)
    if r:
        for event in device.read():
            if event.value == 1 and event.code == 0x02:
                right = True
            elif event.value == 1 and event.code == 0x03:
                left = True
    return left, right


class Face_Recognizer:
    def __init__(self, threshold = 0.5, nms = 0.3, max_face_num = 1):
        model = "retinaface.mud"
        model_fe = "fe_resnet.mud"
        self.input_size = (224, 224, 3)
        input_size_fe = (128, 128, 3)
        self.feature_len = 256
        self.features = []
        print("-- load model:", model)
        m = nn.load(model)
        print("-- load ok")
        print("-- load model:", model_fe)
        m_fe = nn.load(model_fe)
        print("-- load ok")

        self.recognizer = FaceRecognize(m, m_fe, self.feature_len, self.input_size, threshold, nms, max_face_num)
        print("-- init end")

    def get_faces(self, img, std_img = False):
        faces = self.recognizer.get_faces(img, std_img)
        return faces

    def __len__(self):
        return len(self.features)

    def add_user(self, name, feature):
        self.features.append([name, feature])
        return True

    def remove_user(self, name_del):
        rm = None
        for name, feature in self.features:
            if name_del == name:
                rm = [name, feature]
        if rm:
            self.features.remove(rm)
            return True
        return False

    def recognize(self, feature):
        max_score = 0
        uid = -1
        for i, user in enumerate(self.features):
            score = self.recognizer.compare(user[1], feature)
            if score > max_score:
                max_score = score
                uid = i
        if uid >= 0:
            return self.features[uid][0], max_score
        return None, 0


    def get_input_size(self):
        '''
            @return input_size (w, h, c)
        '''
        return self.input_size

    def get_feature_len(self):
        return self.feature_len

    def darw_info(self, img, box, points, disp_str, bg_color=(255, 0, 0, 255), font_color=(255, 255, 255, 255), font_size=32):
        font_wh = image.get_string_size(disp_str)
        for p in points:
            img.draw_rectangle(p[0] - 1, p[1] -1, p[0] + 1, p[1] + 1, color=bg_color)
        img.draw_rectangle(box[0], box[1], box[0] + box[2], box[1] + box[3], color=bg_color, thickness=2)
        if disp_str:
            img.draw_rectangle(box[0], box[1] - font_wh[1], box[0] + font_wh[0], box[1], color=bg_color, thickness = -1)
            img.draw_string(box[0], box[1] - font_wh[1], disp_str, color=font_color)


    def darw_title(self, img, dis_size ,key_l = None, key_r =None):
        if key_l :
            key_l = "| "+ key_l
            img.draw_string( 1, 2 ,key_l , scale = 1, color = (255, 255, 255), thickness = 2)
        if key_r:
            key_r = key_r+" |"
            w = int(dis_size[0] - 4 - image.get_string_size(key_r)[0] * 1)
            img.draw_string( w, 2 ,key_r , scale = 1, color = (255, 255, 255), thickness = 2)



max_face_num = 4
detect_threshold = 0.5
detect_nms = 0.3
score_threshold = 70
names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

face_recognizer = Face_Recognizer(detect_threshold, detect_nms, max_face_num = max_face_num)
camera.config(size=face_recognizer.get_input_size()[:2])

keys_device = InputDevice('/dev/input/event0')
def key_pressed():
    l, r = get_keys(keys_device)
    return l, r

key_l = False
key_r = False


while 1:
    img = camera.capture().resize(size=face_recognizer.get_input_size()[:2])
    if not img:
        time.sleep(0.02)
        continue
    faces = face_recognizer.get_faces(img)
    l, r = key_pressed()
    key_l = l | key_l
    key_r = r | key_r


    face_recognizer.darw_title(img , face_recognizer.get_input_size()[:2] , "rm" ,"add")

    if faces:
        # for prob, box, landmarks, feature, std_img in faces:
        for prob, box, landmarks, feature in faces:
            # [ prob, [x,y,w,h], [[x,y], [x,y], [x,y], [x,y], [x,y]], feature ]
            if key_r:
                if len(face_recognizer) < len(names):
                    idx = len(face_recognizer)
                    print("add user: {}, {}".format(idx, names[idx]))
                    face_recognizer.add_user(names[idx], feature)
                else:
                    print("user full")
                key_r = False
            name, score = face_recognizer.recognize(feature)
            if name:
                if score > score_threshold:
                    face_recognizer.darw_info(img, box, landmarks, "{}:{:.2f}".format(name, score), font_color=(0, 0, 255, 255), bg_color=(0, 255, 0, 255))
                    print("user: {}, score: {:.2f}".format(name, score))
                else:
                    face_recognizer.darw_info(img, box, landmarks, "{}:{:.2f}".format(name, score), font_color=(255, 255, 255, 255), bg_color=(255, 0, 0, 255))
                    print("maybe user: {}, score: {:.2f}".format(name, score))
            else:
                face_recognizer.darw_info(img, box, landmarks, "", font_color=(255, 255, 255, 255), bg_color=(255, 255, 255, 255))

    if key_l:
        if len(face_recognizer) > 0:
            idx = len(face_recognizer) - 1
            print("remove user:", names[idx])
            face_recognizer.remove_user(names[idx])
        else:
            print("user empty")
        key_l = False
    display.show(img)