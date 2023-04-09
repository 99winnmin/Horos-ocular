import boto3
import cv2
from pytube import YouTube

def download():
    # 킹스맨
    url = "https://www.youtube.com/watch?v=k0DKHKCWMuA"

    yt = YouTube(url)
    print("제목 : ", yt.title)
    print("길이 : ", yt.length)
    print("게시자 : ", yt.author)
    print("게시날짜 : ", yt.publish_date)
    print("조회수 : ", yt.views)
    print("키워드 : ", yt.keywords)
    print("설명 : ", yt.description)
    print("썸네일 : ", yt.thumbnail_url)

    video = yt.streams.get_highest_resolution()
    video.download("C:\\Users\\ojyse\\PycharmProjects\\HorusOculars\\resource\\video")

    return video


