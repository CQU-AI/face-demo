# python3
# -*- coding: utf-8 -*-
# @File    : face.py
# @Desc    :
# @Project : face
# @Time    : 10/12/19 7:43 PM
# @Author  : Loopy
# @Contact : peter@mail.loopy.tech
# @License : CC BY-NC-SA 4.0 (subject to project license)

import os
import base64
import time
import json
import requests
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from PIL import Image, ImageDraw
from photo import take_photo


class BaiduPicIndentify:
    def __init__(self, img):
        self.AK = "－－请在此输入你自己的ＡＫ－－"
        self.SK = "－－请在此输入你自己的ＳＫ－－"
        self.img_src = img
        self.headers = {"Content-Type": "application/json; charset=UTF-8"}
        if self.AK == "－－请在此输入你自己的ＡＫ－－" or self.AK == "－－请在此输入你自己的ＳＫ－－":
            raise ConnectionRefusedError("你没有填入BaiduApi的key!请前往百度云平台申请")

    def get_accessToken(self):
        host = (
            "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id="
            + self.AK
            + "&client_secret="
            + self.SK
        )
        response = requests.get(host, headers=self.headers)
        json_result = json.loads(response.text)
        return json_result["access_token"]

    def img_to_BASE64(slef, path):
        with open(path, "rb") as f:
            base64_timestp = base64.b64encode(f.read())
            return base64_timestp

    def detect_face(self):
        # 人脸检测与属性分析
        img_BASE64 = self.img_to_BASE64(self.img_src)
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        post_timestp = {
            "image": img_BASE64,
            "image_type": "BASE64",
            "face_field": "gender,age,beauty,gender,face_shape,landmark",
            "face_type": "LIVE",
        }
        access_token = self.get_accessToken()

        request_url = request_url + "?access_token=" + access_token
        response = requests.post(
            url=request_url, data=post_timestp, headers=self.headers
        )
        json_result = json.loads(response.text)
        if json_result["error_msg"] != "pic not has face":
            result = {
                "age": json_result["result"]["face_list"][0]["age"],
                "score": json_result["result"]["face_list"][0]["beauty"],
                "gender": json_result["result"]["face_list"][0]["gender"]["type"],
                "shape": json_result["result"]["face_list"][0]["face_shape"]["type"],
                "shape_score": json_result["result"]["face_list"][0]["face_shape"][
                    "probability"
                ],
            }
            dic = {
                "male": "男",
                "female": "女",
                "square": "方脸",
                "triangle": "瓜子脸",
                "oval": "椭圆脸",
                "heart": "心型脸",
                "round": "纯圆脸",
            }
            result["shape"] = dic[result["shape"]]
            result["gender"] = dic[result["gender"]]
            # age, score, gender, shape, shape_score
            landmark72 = json_result["result"]["face_list"][0]["landmark72"]
            img = Image.open(self.img_src)
            draw = ImageDraw.Draw(img)
            for idx in range(72):
                xy = landmark72[idx]
                draw.text((xy["x"], xy["y"]), "^", (255, 0, 0))
            ImageDraw.Draw(img)
            img.save(str(self.img_src).replace("static/", "static/new_"))
            if result["shape"] == "纯圆脸" and result["shape_score"] > 0.7:
                result = {
                    "age": "请勿上传盘子!!!",
                    "score": "请勿上传盘子!!!",
                    "gender": "请勿上传盘子!!!",
                    "shape": "请勿上传盘子!!!",
                    "shape_score": "请勿上传盘子!!!",
                }
            return result
        else:
            return "未识别出人脸"


def get_face_score(img_src):
    baiduDetect = BaiduPicIndentify(
        os.path.join(os.path.join(os.getcwd(), "static"), img_src)
    )
    return baiduDetect.detect_face()


########################################################################################################################
# flask
app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = "./faces"
app.config["UPLOADED_PHOTOS_DEST"] = os.path.join(os.getcwd(), "static")
# app.config['UPLOAD_PHOTOS_DEST'] = 'static'
photos = UploadSet("photos", IMAGES)
configure_uploads(app, photos)
patch_request_class(app)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST" and "photo" in request.files:
        timestp = str(int(float(time.time())))
        filename = secure_filename(photos.save(request.files["photo"]))
        os.rename(
            "static/" + str(filename),
            "static/" + timestp + "." + str(filename).split(".")[-1],
        )
        filename = timestp + "." + str(filename).split(".")[-1]
        file_url = photos.url(filename)
        content = get_face_score(filename)
        new_url = photos.url("new_" + filename)
        return render_template(
            "result.html", file_url=file_url, new_url=new_url, content=content
        )
    return render_template("result.html")


@app.route("/photo", methods=["GET", "POST"])
def index_photo():
    timestp = str(int(float(time.time())))
    filename = "{}.jpg".format(timestp)
    take_photo("./static/" + filename)
    file_url = photos.url(filename)
    content = get_face_score(filename)
    new_url = photos.url("new_" + filename)
    return render_template(
        "result.html", file_url=file_url, new_url=new_url, content=content
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
