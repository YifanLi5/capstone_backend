import sqlite3
import json

class SlideshowSqlHandler:
    def __init__(self):
        self.conn = sqlite3.connect('s3.db')

    #for inserting into db from a json file
    def insert_assets_from_file(self, json_file_path):
        json_file = open(json_file_path)
        json_data = json.load(json_file)

        self.conn.execute('CREATE TABLE IF NOT EXISTS SLIDESHOW (upload_time INT PRIMARY KEY NOT NULL, asset_url TEXT, text TEXT)')
        slide_show_list = json_data['example_slideshow']
        database_insert = []
        for item in slide_show_list:
            upload_time = item['upload_time']
            cursor = self.conn.execute('SELECT upload_time from SLIDESHOW where upload_time=?', (upload_time,))
            data = cursor.fetchone()
            if data is None:
                database_insert.append((upload_time, item['asset_url'], item['text']))
        self.conn.executemany('INSERT INTO SLIDESHOW VALUES (?,?,?)', database_insert)
        self.conn.commit()

    #insert by passing in folder_asset object
    def insert_from_folder_asset(self, folder_asset):
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS SLIDESHOW (upload_time INT PRIMARY KEY NOT NULL, asset_url TEXT, text TEXT)')
        upload_time = folder_asset.upload_time
        cursor = self.conn.execute('SELECT upload_time from SLIDESHOW where upload_time=?', (upload_time,))
        data = cursor.fetchone()

        inserted = data is None
        if inserted:
            assert_url = folder_asset.asset_url
            text = folder_asset.text
            self.conn.execute("INSERT INTO SLIDESHOW (upload_time, asset_url, text) VALUES (?,?,?)", (upload_time, assert_url, text,))
            self.conn.commit()

        return inserted

    def retrieve_all(self):
        json_data = {}
        slideshow = []
        cursor = self.conn.execute('SELECT upload_time, asset_url, text from SLIDESHOW')
        for row in cursor:
            slideshow_entry = {}
            slideshow_entry['upload_time'] = row[0]
            slideshow_entry['asset_url'] = row[1]
            slideshow_entry['text'] = row[2]
            slideshow.append(slideshow_entry)

        json_data['slideshow'] = slideshow

        return json_data

    def retrieve_after_timestamp(self, timestamp):
        json_data = {}
        slideshow = []
        cursor = self.conn.execute('SELECT upload_time, asset_url, text from SLIDESHOW')
        for row in cursor:
            upload_time = row[0]
            if upload_time >= timestamp:
                slideshow_entry = {}
                slideshow_entry['upload_time'] = row[0]
                slideshow_entry['asset_url'] = row[1]
                slideshow_entry['text'] = row[2]
                slideshow.append(slideshow_entry)

        json_data['slideshow'] = slideshow
        return json_data
