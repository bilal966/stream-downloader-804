import os
import math
from moviepy.editor import VideoFileClip
from flask import Flask, request, send_file
from flask import render_template
from server.utils.ytVideoDownloader import YouTubeVideoDownloader
from server.utils.downloadBySearch import DownloadBySearch
from pytube.helpers import regex_search
from pytube.exceptions import RegexMatchError

# create app instance
# app = Flask(__name__)
app = Flask(
        __name__,
        template_folder='client/templates',
        static_folder='client/static'
    )

# secret key
app.config['SECRET_KEY'] = "AIzaSyDBsTomCrzkKxpLdFnYcdhOWkVFSu-DNnU"

# methods
methods = ['POST', "GET"]

# routes
home_route = '/'

# Log prefix
log_prefix = 'stream-downloader804-'

# generate content directory
app_directory = os.path.abspath(os.getcwd())
video_content_path = app_directory + "/video_content"
videos_path = video_content_path+"/videos"
clips_path = video_content_path+"/clips"
isExist = os.path.exists(videos_path)
if not isExist:
    os.makedirs(videos_path)
isExist = os.path.exists(clips_path)
if not isExist:
    os.makedirs(clips_path)

@app.route(home_route, methods=["GET"])
def home():
    return render_template('v3.html', error=None, data=None)


@app.route("/getBasicDetails", methods=["POST"])
def getBasicDetails():
    video_url = request.get_json()['video-url']
    # print(video_url)
    try:
        yt = YouTubeVideoDownloader(video_url).getBasicDetails()
        print(log_prefix, "video basic data: ", yt)
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
        video_id = regex_search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url, group=1)
        stream = YouTubeVideoDownloader(video_url).downloadByItag(itag)
        print(log_prefix, video_id,stream,stream.default_filename)

        #Signed video url
        video_url = stream.url
        # Load the video from the URL
        video = VideoFileClip(video_url)

        # Define the start and end times (in seconds) for the segment you want to cut
        start_time = 10  # start at 10 seconds
        end_time = 30  # end at 30 seconds

        # Cut the video
        cut_video = video.subclip(time_start, time_end)
        # downloadable file name
        video_filename = str(itag) + "_" + time_start + "_" + time_end + "_" + video_id+".mp4"
        video_file_path = videos_path+'/'+video_filename
        if os.path.exists(video_file_path):
            print(log_prefix, "File exists.", video_filename)
        else:
            print(log_prefix, "File does not exist.",video_filename)
            # Save the cut video to a file
            cut_video.write_videofile(video_file_path, audio_codec='aac', threads=4)
        cut_video.close()
        # response = send_file(f"{video_filename}", as_attachment=True)
        # os.remove(f"{video_filename}")
        return {"status": True, "url": stream.url, "file_name": video_filename}
    except:
        return {"status": False}




@app.route('/downloadCroppedVideo', methods=["GET"])
def downloadCroppedVideo():
    print(log_prefix, "Start downloading cropped video")
    video_filename = request.args.get("file_name")
    try:
        # downloadable file name
        response = send_file(f"{videos_path+'/'+video_filename}", as_attachment=True,etag=False)
        # os.remove(f"{video_filename}")
        return response
    except:
        return {"Status":False, "ErrorMessage":"Internal Server Error.File not available."}


@app.route('/cutVideoClips', methods=["GET"])
def cutVideoClips():
    print(log_prefix, "Start cutting video into clips.")
    video_filename = 'WcJwYVEarXs_dchowk_protest.mp4'
    video_id = 'WcJwYVEarXs'
    video_clips_path = clips_path+'/'+video_id
    try:
        fullDuration = VideoFileClip(videos_path+'/'+video_filename).duration
        print('Video file duration in seconds:', fullDuration)
        # clip length in seconds
        clipDuration = 180
        no_of_clips = math.floor(fullDuration/clipDuration)
        single_duration = fullDuration / no_of_clips
        print('Start generating video clips process.')
        isExist = os.path.exists(video_clips_path)
        if not isExist:
            os.makedirs(video_clips_path)

        while no_of_clips > 0:
            print('Preparing video clip:'+str(no_of_clips))
            clip = VideoFileClip(videos_path+'/'+video_filename)
            if(no_of_clips==1):
                clip = clip.subclip(0, fullDuration)
            else:
                clip = clip.subclip(fullDuration - single_duration, fullDuration)
                fullDuration -= single_duration

            clip_file_name = 'Part_'+str(no_of_clips)+'_'+video_id+'_.mp4'
            print(clip_file_name)
            clip.write_videofile(video_clips_path+'/'+clip_file_name, audio_codec='aac', threads=4)
            no_of_clips = no_of_clips - 1

        print('Finished generating clips process.')
        return {"Video id": video_id, 'File Name': video_filename}
    except:
        return {"Status":False, "ErrorMessage":"Internal Server Error.File not available."}


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


