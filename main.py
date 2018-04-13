#NEEDS PYTHON2 NOT 3
import boto3
from flask import Flask, json  # pip install flask
from flask import jsonify
from flask import request
import folder_asset
import timeline_asset
import s3_sql_handler
import s3_rest_handler
import timeline_sql_handler
import platform

app = Flask(__name__)
app.json_encoder = folder_asset.FolderAssetJSONEncoder

s3_slideshow_url = 'http://psyche-andromeda.s3.amazonaws.com/example_slideshow/'
general_upload_folder = 'example_slideshow/'
s3_timeline_url = 'http://psyche-andromeda.s3.amazonaws.com/timeline/'
timeline_upload_folder = 'timeline/'


@app.route('/')
def base_page_handler():
    return  "api:" \
            "\n" \
            "GET /everything\n" \
            "returns every asset in s3" \
            "\n\n" \
            "GET /filter?=[unix_timestamp]\n" \
            "returns every asset uploaded after [unix_timestamp] argument" \
            "\n\n" \
            "GET /timeline \n" \
            "returns the mission timeline" \
            "\n\n" \
            "POST /upload \n" \
            "send a multipart form-data request with [key]::[values]\n" \
            "ex: entry is a key, the value is json str of relevant information to pass in\n" \
            "entry::(see /upload_json.txt)\n" \
            "file::[image file].jpg or .jpeg or .png" \
            "\n\n" \
            "POST /timeline_update \n" \
            "send a multipart form-data request with [key]::[values]\n" \
            "entry::(see /timeline_update_json.txt)\n" \
            "file0::[image file].jpg or .jpeg or .png\n" \
            "file1::[image file].jpg or .jpeg or .png\n" \
            "file2::[image file].jpg or .jpeg or .png\n" \
            "submit as many files as needed for the specified timeline entry, ensure that media array in the json sent under the \"entry\"\n" \
            "matches how many files you are submitting."


@app.route('/everything', methods = ['GET'])
def everything_page_handler():
    output = s3_sql_handler.SlideshowSqlHandler().retrieve_all()
    return jsonify(output)

@app.route('/filter', methods = ['GET'])
def filter_page_handler():
    last_update_timestamp = request.args.get('last_update', default=0, type=long)
    output = s3_sql_handler.SlideshowSqlHandler().retrieve_after_timestamp(last_update_timestamp)
    return jsonify(output)

@app.route('/timeline', methods = ['GET'])
def timeline_handler():
    output = timeline_sql_handler.TimelineSQLHandler().retrieve_timeline()
    return jsonify(output)

@app.route('/upload', methods = ['POST'])
def upload_handler():
    raw_json_data = request.form.get('entry')
    if raw_json_data:
        json_data = json.loads(raw_json_data)
        #s3_slideshow_url string appended to the the image name string gives the url that s3 will place the image.
        #the first arguement into the upcoming constructor is the image url.
        url = s3_slideshow_url + json_data['image_name']
        new_asset = folder_asset.FolderAsset(url, json_data['upload_time'], json_data['text'])
        is_new = s3_sql_handler.SlideshowSqlHandler().insert_from_folder_asset(new_asset)
        if is_new:
            image_data = request.files.get('file', '')
            if image_data:
                s3 = boto3.resource('s3')
                print("uploading to: " + general_upload_folder + json_data['image_name'])
                s3.Bucket('psyche-andromeda').put_object(Key=general_upload_folder + json_data['image_name'], Body=image_data)

                return "200 success" \
                       "\nasset_url: " + url + \
                       "\nupload_time: " + str(json_data['upload_time']) + \
                       "\ntext: " + json_data['text']
    return "TODO: other error codes"

@app.route('/timeline_update', methods = ['POST'])
def timeline_update_handler():
    raw_json_data = request.form.get('entry')
    if raw_json_data:
        json_data = json.loads(raw_json_data)
        dateTime = json_data['dateTime']
        name = json_data['name']
        description = json_data['description']
        media = json_data['media']

        filetypes = []
        asset_url = []
        for item in media:
            temp = item['filename']
            if temp.endswith('.jpg') or temp.endswith('.jpeg') or temp.endswith('png'):
                idx = temp.rfind('.')
                filetypes.append(temp[idx:])
                asset_url.append(s3_timeline_url + temp)
            else:
                return "400 client error" \
                        "\nfilename " + item + " not a jpeg, jpg, or png"
        asset = timeline_asset.TimelineAsset(dateTime, name, description, filetypes, asset_url)
        is_new = timeline_sql_handler.TimelineSQLHandler().insert_from_timeline_obj(asset)
        if True:
            for item in media:
                temp = item['filename']
                image_data = request.files.get(temp, '')
                if image_data:
                    s3 = boto3.resource('s3')
                    print("uploading to: " + timeline_upload_folder + temp)
                    s3.Bucket('psyche-andromeda').put_object(Key=timeline_upload_folder + temp,
                                                             Body=image_data)
            return "200 success" \
                   "\ndateTime: " + dateTime + \
                   "\nname: " + temp + \
                   "\ndescription: " + description + \
                   "\nmedia_urls: " + ''.join(asset_url)

    return "TODO: other error codes"

def setup():
    test_asset = timeline_asset.TimelineAsset("datetime", "name", "desc", [".png", ".jpeg"], ["link1", "link2"])
    timeline_sql_handler.TimelineSQLHandler().insert_from_timeline_obj(test_asset)

def main():
    #setup()
    if platform.system() == "Linux":
        app.run(host='0.0.0.0', port=8080, debug=True)
    elif platform.system() == "Windows":
        app.run(host='0.0.0.0', port=50000, debug=True)





if __name__ == "__main__":
    main()
