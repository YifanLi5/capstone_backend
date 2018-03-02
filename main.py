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

@app.route('/everything')
def everything_page_handler():
    sql = s3_sql_handler.SlideshowSqlHandler()
    sql.insert_s3_if_needed('everything.json')
    output = sql.retrieve()
    return jsonify(output)

@app.route('/filter')
def filter_page_handler():
    last_update_timestamp = request.args.get('last_update', default=0, type=long)
    sql = s3_sql_handler.SlideshowSqlHandler()
    sql.insert_s3_if_needed('everything.json')
    output = sql.retrieve_after_timestamp(last_update_timestamp)
    return jsonify(output)

@app.route('/timeline')
def timeline():
    sql = timeline_sql_handler.TimelineSQLHandler()
    sql.insert_timeline_if_needed('sample_timeline1.json')
    output = sql.retrieve_timeline()
    return jsonify(output)


def main():

    if platform.system() == "Linux":
        app.run(host='0.0.0.0', port=5000, debug=True)
        # If the system is a windows /!\ Change  /!\ the   /!\ Port
    elif platform.system() == "Windows":
        app.run(host='0.0.0.0', port=50000, debug=True)




if __name__ == "__main__":
    main()
