import subprocess, os
from moviepy.editor import VideoFileClip
from flask import Flask, request, send_file
from flask import render_template
from youtube_transcript_api import YouTubeTranscriptApi
from utils.ytVideoDownloader import YouTubeVideoDownloader
from utils.downloadBySearch import DownloadBySearch

from pytube.exceptions import RegexMatchError

# create app instance
app = Flask(__name__)

# secret key
app.config['SECRET_KEY'] = "AIzaSyDAs1GMYdmiF2JVXpdInFnsVK65Dr3vY98"

# methods
methods = ['POST', "GET"]

# routes
home_route = '/'


@app.route(home_route, methods=["GET"])
def home():
    return render_template('v3.html', error=None, data=None)


@app.route("/getBasicDetails", methods=["POST"])
def getBasicDetails():
    video_url = request.get_json()['video-url']
    # print(video_url)
    try:
        yt = YouTubeVideoDownloader(video_url).getBasicDetails()
        print("basic data: ", yt)
        return yt
    except RegexMatchError:
        return {"status": False}


@app.route("/getStreamsData", methods=["POST"])
def getStreamsData():
    video_url = request.get_json()['video-url']
    print("Video URL to Download:", video_url)
    yt = YouTubeVideoDownloader(video_url).getStreamsData()
    # transcript = YouTubeTranscriptApi.get_transcript('d5Ryd34kJVE')
    # print(transcript)

    return yt


@app.route('/downloadByItag', methods=["POST"])
def downloadByItag():
    itag = request.get_json()['itag']
    video_url = request.get_json()['video-url']
    stream = YouTubeVideoDownloader(video_url).downloadByItag(itag)
    print(stream.default_filename)

    video_url = stream.url
    # Load the video from the URL
    video = VideoFileClip(video_url)

    # Define the start and end times (in seconds) for the segment you want to cut
    start_time = 10  # start at 10 seconds
    end_time = 30  # end at 30 seconds

    # Cut the video
    cut_video = video.subclip(start_time, end_time)
    # downloadable file name
    video_filename = str(itag) + "_" + stream.default_filename.replace(" ", "_")
    # Save the cut video to a file
    cut_video.write_videofile(video_filename, audio_codec='aac')
    response = send_file(f"{video_filename}", as_attachment=True)
    os.remove(f"{video_filename}")
    return {"url": stream.url}


@app.route('/downloadClipByItag', methods=["POST"])
def downloadClipByItag():
    itag = request.get_json()['itag']
    video_url = request.get_json()['video-url']
    time_start = request.get_json()['time_start']
    time_end = request.get_json()['time_end']
    stream = YouTubeVideoDownloader(video_url).downloadByItag(itag)
    print(stream.default_filename)

    video_url = stream.url
    # Load the video from the URL
    video = VideoFileClip(video_url)

    # Define the start and end times (in seconds) for the segment you want to cut
    start_time = 10  # start at 10 seconds
    end_time = 30  # end at 30 seconds

    # Cut the video
    cut_video = video.subclip(time_start, time_end)
    # downloadable file name
    video_filename = str(itag) + "_" + stream.default_filename.replace(" ", "_")
    # Save the cut video to a file
    cut_video.write_videofile(video_filename, audio_codec='aac')
    response = send_file(f"{video_filename}", as_attachment=True)
    # os.remove(f"{video_filename}")
    # return {"url": stream.url}
    return response


@app.route('/downloadCroppedVideo', methods=["GET"])
def downloadCroppedVideo():
    print("Start downloading cropped video")
    # downloadable file name
    video_filename = "18_Massive_Public_on_Roads_Protest_for_Khan-_Aitchison_College_Refused_Entry_of_Maryam_Safdar.mp4"
    response = send_file(f"{video_filename}", as_attachment=True)
    # os.remove(f"{video_filename}")
    return response


@app.route('/searchVideo', methods=['POST'])
def searchVideo():
    video_name = request.get_json()["search-video-name"]

    try:
        return {
            "status": True,
            "search_data": DownloadBySearch(video_name).search()
        }
    except:
        return {
            "status": False
        }


if __name__ == "__main__":
    app.run(debug=True, port="5000")

