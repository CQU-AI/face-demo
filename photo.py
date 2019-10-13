# python3
# -*- coding: utf-8 -*-
# @File    : photo.py
# @Desc    :
# @Project : face
# @Time    : 10/12/19 9:53 PM
# @Author  : Loopy
# @Contact : peter@mail.loopy.tech
# @License : CC BY-NC-SA 4.0 (subject to project license)

import cv2


def take_photo(filepath):
    cap = cv2.VideoCapture(0)
    i = 0
    while True:
        ret, frame = cap.read()

        # cv2.imshow("Press space to take a photo", frame)
        if cv2.waitKey(1) & 0xFF == ord(" ") or i > 5:
            cv2.imwrite(filepath, frame)
            break
        i += 1
        print(i)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    take_photo("./1.jpg")
    take_photo("./2.jpg")
