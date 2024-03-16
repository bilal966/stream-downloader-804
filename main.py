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
app.config['SECRET_KEY'] = ""

# methods
methods = ['POST', "GET"]

# routes
home_route = '/'

# Log prefix
log_prefix = 'StreamDownloader804- '

@app.route(home_route, methods=["GET"])
def home():
    return render_template('v3.html', error=None, data=None)


@app.route("/getBasicDetails", methods=["POST"])
def getBasicDetails():
    video_url = request.get_json()['video-url']
    # print(video_url)
    try:
        yt = YouTubeVideoDownloader(video_url).getBasicDetails()
        print(log_prefix, "basic data: ", yt)
        return yt
    except RegexMatchError:
        return {"status": False}


@app.route("/getStreamsData", methods=["POST"])
def getStreamsData():
    video_url = request.get_json()['video-url']
    print(log_prefix, "Video URL to Download:", video_url)
    yt = YouTubeVideoDownloader(video_url).getStreamsData()
    # transcript = YouTubeTranscriptApi.get_transcript('d5Ryd34kJVE')
    # print(transcript)

    return yt


@app.route('/downloadByItag', methods=["POST"])
def downloadByItag():
    itag = request.get_json()['itag']
    video_url = request.get_json()['video-url']
    stream = YouTubeVideoDownloader(video_url).downloadByItag(itag)
    print(log_prefix, stream.default_filename)
    return {"url": stream.url}


@app.route('/downloadClipByItag', methods=["POST"])
def downloadClipByItag():
    itag = request.get_json()['itag']
    video_url = request.get_json()['video-url']
    time_start = request.get_json()['time_start']
    time_end = request.get_json()['time_end']

    try:
        stream = YouTubeVideoDownloader(video_url).downloadByItag(itag)
        print(log_prefix, stream.default_filename)

        video_url = stream.url
        # Load the video from the URL
        video = VideoFileClip(video_url)

        # Define the start and end times (in seconds) for the segment you want to cut
        start_time = 10  # start at 10 seconds
        end_time = 30  # end at 30 seconds

        # Cut the video
        cut_video = video.subclip(time_start, time_end)
        # downloadable file name
        video_filename = str(itag) + "_" + time_start + "_" + time_end + "_" + stream.default_filename.replace(" ", "_")
        if os.path.exists(video_filename):
            print(log_prefix, "File exists.", video_filename)
        else:
            print(log_prefix, "File does not exist.")
            # Save the cut video to a file
            cut_video.write_videofile(video_filename, audio_codec='aac')

        # response = send_file(f"{video_filename}", as_attachment=True)
        # os.remove(f"{video_filename}")
        return {"status": True, "url": stream.url, "file_name": video_filename}
    except:
        return {"status": False}




@app.route('/downloadCroppedVideo', methods=["GET"])
def downloadCroppedVideo():
    print(log_prefix, "Start downloading cropped video")
    video_filename = request.args.get("file_name")
    # downloadable file name
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
    app.run(debug=True, port="5001")

