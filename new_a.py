# -*- coding:utf-8 -*-

#コメントを外して最後まで通った

import json
import falcon
import mysql_operationfix as mo
import datetime
import os

data_path = "./File"
today = str(datetime.date.today()).split('-')
year = today[0][2:4]
year_path = "./File/data/" + year + "/"
month = today[1]
month_path = year_path + month + "/"
date = today[2]
date_path = month_path + date + "/"
raw_path = date_path + "raw/"

class report(object):

    def on_post(self, req, res):
        body = req.stream.read()
        data = json.loads(body.decode("utf-8"))
        db = mo.MySQLConnect(user="root",passwd="naoya0817",charset="utf8",db="user")
        #db = mo.MySQLConnect(user="root",passwd="naoya0817",charset="utf8",db="data") dbの部分の訂正(data->user)
        userAuth = db.db_result('select accesstoken from auth where userid="' + data["user"]["userid"]+ '"')

        if(userAuth[0]["accesstoken"] == data["user"]["access_token"]):
            #idの確認ができない
            #if(userAuth[0]["userid"]) == data["user"]["userid"]:   #userAuth[0]["userid"]は存在しない
                db.db_close()
                db = mo.MySQLConnect(user="root",passwd="naoya0817",charset="utf8",db="hist")
                db.db_insert(table="report",data={
                    "comment":data["user"]["comment"],
                    "name":data["user"]["userid"],
                    "os": data["user"]["os"],
                    "ip": data["user"]["ip"],
                    "pcuser":data["user"]["pcuser"],
                    "date":"now()",
                    #####type はmacadress!!##########
                    "type": data["user"]["macadress"]
            })

#create_path
        if os.path.exists(year_path) == False:
            os.mkdir(year_path)
            if os.path.exists(month_path) == False:
                os.mkdir(month_path)
                if os.path.exists(date_path) == False:
                    os.mkdir(date_path)
                    if os.path.exists(raw_path) == False:
                        os.mkdir(raw_path)
                    else:
                        pass
                else:
                    if os.path.exists(raw_path) == False:
                        os.mkdir(raw_path)
            else:
                if os.path.exists(date_path) == False:
                    os.mkdir(date_path)
                if os.path.exists(raw_path) == False:
                    os.mkdir(raw_path)
        else:
            if os.path.exists(month_path) == False:
                os.mkdir(month_path)
            if os.path.exists(date_path) == False:
                os.mkdir(date_path)
            if os.path.exists(raw_path) == False:
                os.mkdir(raw_path)

#data_db
        db = mo.MySQLConnect(user="root",passwd="naoya0817",charset="utf8",db="data")
        #テーブル名作成
        result = db.db_result(string="show tables")
        for i in range(len(result)):
            result[i] = result[i]["Tables_in_data"]

        #テーブル存在確認/作成
        for i in range(len(data["statuses"])):
            data2 = "id" + str(data["statuses"][i]["user"]["id"])
            if data2 in result:
                print("data2 exist")
            else:
                print("data2 not exist")
                #テーブル作成
                db.db_query(string="create table " + data2 + "( created_at varchar(255), default_profile varchar(255), default_profile_image varchar(255), description varchar(255), favourites_count varchar(255), followers_count varchar(255), friends_count varchar(255), id varchar(255), lang varchar(255), listed_count varchar(255), location varchar(255), name varchar(255), profile_background_image_url varchar(255), profile_image_url varchar(255), screen_name varchar(255),statuses_count varchar(255), time_zone varchar(255), url varchar(255), utc_offset varchar(255), verified varchar(255) ,good varchar(255),bad varchar(255),rank varchar(255));");

        for j in range(len(data["statuses"])):
            data2 = "id" + str(data["statuses"][j]["user"]["id"])
            post_data = data["statuses"][j]["user"]
            #最新のテーブル取得
            latest = db.db_result(string="select * from " + data2 + " order by id desc limit 1")
            for i in post_data:
                if type(post_data[i]) == bool:
                    if post_data[i] == True:
                        post_data[i] = "1"
                    else:
                        post_data[i] = "0"
            #すべてのvalueが一致しているか
            if (len(latest) > 0)and(latest[0]["default_profile_image"] == post_data["default_profile_image"])and(latest[0]["description"] == post_data["description"])and(latest[0]["followers_count"] == post_data["followers_count"])and(latest[0]["friends_count"] == post_data["friends_count"])and(latest[0]["name"] == post_data["name"])and(latest[0]["profile_background_image_url"] == post_data["profile_background_image_url"])and(latest[0]["profile_image_url"] == post_data["profile_image_url"])and(latest[0]["screen_name"] == post_data["screen_name"])and(latest[0]["statuses_count"] == post_data["statuses_count"])and(latest[0]["profile_image_url"] == post_data["profile_image_url"])and(latest[0]["url"] == post_data["url"]):
                print("agree")
            else:
                print("disagree")
                #最新のテーブルとポストされた値が一致しないかつ、テーブルの中身が存在しない
                db.db_insert(table=data2,data={
                    "created_at": str(data["statuses"][j]["user"]["created_at"]),
                    "default_profile": str(data["statuses"][j]["user"]["default_profile"]),
                    "default_profile_image": str(data["statuses"][j]["user"]["default_profile_image"]),
                    "favourites_count": str(data["statuses"][j]["user"]["favourites_count"]),
                    "description": str(data["statuses"][j]["user"]["description"]),
                    "followers_count": str(data["statuses"][j]["user"]["followers_count"]),
                    "friends_count": str(data["statuses"][j]["user"]["friends_count"]),
                    "id": str(data["statuses"][j]["user"]["id"]),
                    "lang": str(data["statuses"][j]["user"]["lang"]),
                    "listed_count": str(data["statuses"][j]["user"]["listed_count"]),
                    "location": str(data["statuses"][j]["user"]["location"]),
                    "name": str(data["statuses"][j]["user"]["name"]),
                    "profile_background_image_url": str(data["statuses"][j]["user"]["profile_background_image_url"]),
                    "profile_image_url": str(data["statuses"][j]["user"]["profile_image_url"]),
                    "screen_name": str(data["statuses"][j]["user"]["screen_name"]),
                    "statuses_count": str(data["statuses"][j]["user"]["statuses_count"]),
                    "time_zone": str(data["statuses"][j]["user"]["time_zone"]),
                    "url": str(data["statuses"][j]["user"]["url"]),
                    "utc_offset": str(data["statuses"][j]["user"]["utc_offset"]),
                    "verified": str(data["statuses"][j]["user"]["verified"])
                })

# #tweets_db
        db = mo.MySQLConnect(user="root",passwd="naoya0817",charset="utf8",db="tweets")
        #テーブル名作成
        result = db.db_result(string="show tables")
        for i in range(len(result)):
            result[i] = result[i]["Tables_in_tweets"]
        #テーブル存在確認/作成
        for i in range(len(data["statuses"])):
            data3 = "id" + str(data["statuses"][i]["user"]["id"])
            if data3 in result:
                print("data3 exist")
            else:
                print("data3 not exist")
                #テーブル作成
                db.db_query(string="create table " + data3 + "(tweet_retweet_count varchar(255),tweet_favorite_count varchar(255),tweet_in_reply_to_user_id varchar(255),tweet_in_reply_to_status_id varchar(255),tweet_text varchar(255),tweet_id varchar(255),tweet_created_at varchar(255),created_at varchar(255),default_profile varchar(255),default_profile_image varchar(255),description varchar(255),favourites_count varchar(255),followers_count varchar(255),friends_count varchar(255),id int auto_increment,lang varchar(255),listed_count varchar(255),location varchar(255),name varchar(255)profile_background_image_url varchar(255),profile_image_url varchar(255),screen_name varcahr(255),statuses_count varchar(255),time_zone varchar(255),url varchar(255),utc_offset varchar(255),verified varchar(255),index(id));"
                );
        db.db_close()

#tweet_db
        db = mo.MySQLConnect(user="root",passwd="naoya0817",charset="utf8",db="tweet")
        #テーブル名作成
        result = db.db_result(string="show tables")
        for i in range(len(result)):
            result[i] = result[i]["Tables_in_tweet"]
        #テーブル存在確認/作成
        for j in range(len(data["statuses"])):
            data3 = "id" + str(data["statuses"][j]["user"]["id"])
            tweet_id = str(data["statuses"][j]["id"])
            latest = db.db_result(string="select * from " + data3 + ' where id=' + tweet_id)
            if data3 in result:
                print("data3 exist")
            else:
                print("data3 not exist")
                #デーブル作成
                db.db_query(string="create table " + data3 + "(retweet_count varchar(255),favorite_count varchar(255),in_reply_to_user_id varchar(255),in_reply_to_status_id varchar(255),text varchar(255),id varchar(255) primary key,created_at varchar(255),iso_language_code varchar(255),source varchar(255), lang varchar(255),good int,bad int,index(id));")
                    #idのprimary_keyを外している

        for i in range(len(data["statuses"])):
            tweet = data["statuses"][i]
            for k in tweet:
                if type(tweet[k]) == bool:
                    if tweet[k] == True:
                        tweet[k] = "1"
                    else:
                        tweet[k] = "0"
                if len(latest) == 0:
                    if tweet["flg"] == "none":
                        good = 0
                        bad = 1
                    else:
                        good = 1
                        bad = 0
                    db.db_insert(table=data3,data={
                        "retweet_count" : str(tweet["retweet_count"]),
                        "favorite_count" : str(tweet["favorite_count"]),
                        "in_reply_to_user_id" : str(tweet["in_reply_to_user_id"]),
                        "in_reply_to_status_id" : str(tweet["in_reply_to_status_id"]),
                        "text" : str(tweet["text"]),
                        "created_at" : str(tweet["created_at"]),
                        "id":str(tweet["id"]),
                        "lang" : str(tweet["lang"]),
                        "iso_language_code":str(tweet["metadata"]["iso_language_code"]),
                        "source" : str(tweet["source"]),
                        "good" : good,
                        "bad" : bad
                        })
                else:
                    pass
                    # #flg処理
                    # else:
                    #     if data["statuses"][i]["flg"] == "none":
                    #         db.db_update(table=data3,value={},where={},query="")
                    #     else:
                    #         db.db_update(table=data3,value={},where={},query="")

class route():
    app = falcon.API()
    app.add_route("/report", report())

if __name__ == "__main__":
    from wsgiref import simple_server
    httpd = simple_server.make_server("127.0.0.1", 80, route.app)
    httpd.serve_forever()
