#NEEDS PYTHON2 NOT 3
from flask import Flask #pip install flask
from flask import jsonify
from flask import request
import folder_asset
import s3_sql_handler
import s3_rest_handler
import timeline_sql_handler
import platform

app = Flask(__name__)
app.json_encoder = folder_asset.FolderAssetJSONEncoder

@app.route('/')
def base_page_handler():
    return "api:" \
           "\n" \
           "GET [base_url]/everything\n" \
           "returns every asset in s3" \
           "\n\n" \
           "GET [base_url]/filter?=[unix_timestamp]\n" \
           "returns every asset uploaded after [unix_timestamp] argument" \
           "\n\n" \
           "GET [base_url]/timeline \n" \
           "returns the mission timeline"

@app.route('/everything', methods = ['GET'])
def everything_page_handler():
    output = s3_sql_handler.SlideshowSqlHandler().retrieve()
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
    post_data = request.get_json()
    new_asset = folder_asset.FolderAsset(post_data['asset_url'], post_data['upload_time'], post_data['text'])
    s3_sql_handler.SlideshowSqlHandler().insert_from_folder_asset(new_asset)
    return "200 success" \
           "\nasset_url: " + post_data['asset_url'] + \
           "\nupload_time: " + str(post_data['upload_time']) + \
           "\ntext: " + post_data['text']

def setup():
   timeline_sql_handler.TimelineSQLHandler().insert_assets_from_file('sample_timeline1.json')
   s3_sql_handler.SlideshowSqlHandler().insert_assets_from_file('everything.json')

def main():
    setup()
    if platform.system() == "Linux":
        app.run(host='0.0.0.0', port=8080, debug=True)
    elif platform.system() == "Windows":
        app.run(host='0.0.0.0', port=50000, debug=True)





if __name__ == "__main__":
    main()
