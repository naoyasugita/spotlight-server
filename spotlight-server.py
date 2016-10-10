# -*- coding: utf-8 -*-
# Copyright (c) 2016 NaoyaSugita and MareiKikukawa

##### Import #####

import sys

import os
import json
import datetime
import hashlib
import re

import urllib.parse

# Import a module from a relative path.
sys.path.append( './library' )

# Server
import falcon
from wsgiref import simple_server

# Support
import mysql_connector_wrapper as mcw

##### Arguments #####

# Command line arguments.
# The first argument is host and second argument is port number.
# If argument not specified for parameter, host is A and port number is B.
param = sys.argv

host = str( param[1] ) if len( param ) == 3 else '127.0.0.1'
port = int( param[2] ) if len( param ) == 3 else 3000

##### Connect to MySQL #####

# Default user for MySQL.
user     = 'root'
password = 'pass'

# Connect to database using mysql_connector_wrapper.
def db( name, user=user, password=password ) :
    if not name :
        return False
    return mcw.MySQLConnect( user=user, passwd=password, db=name )

# userdb    = db( 'user' )
# historydb = db( 'history' )
# profiledb = db( 'profile' )
# tweetdb   = db( 'tweet' )

##### Function #####

# Shortcut
exist = os.path.exists
join  = os.path.join
mkdir = os.mkdir

dump  = json.dumps

# Return current time.
def now( option='%Y%m%d%H%M%S' ) :
    return datetime.datetime.now().strftime( option )

# Check directory and if not exist, create new folder.
def checkAndNew() :
    base  = 'files'
    year  = now( '%y' )
    month = now( '%m' )
    day   = now( '%d' )
    try :
        if not exist( join( base, year ) ) :
            mkdir( join( base, year ) )
            mkdir( join( base, year, month ) )
            mkdir( join( base, year, month, day ) )
        else :
            if not exist( join( base, year, month ) ) :
                mkdir( join( base, year, month ) )
                mkdir( join( base, year, month, day ) )
            else :
                if not exist( join( base, year, month, day ) ) :
                    mkdir( join( base, year, month, day ) )
        return [ year, month, day ]
    except :
        return False

# Create new file.
def newFile( filename, text ) :
    try :
        f = open( filename, 'w' )
        f.write( text )
        f.close()
        return True
    except :
        return False

# Create new hash.
def newHash( seed='' ) :
    return hashlib.sha224( seed.encode('utf-8') ).hexdigest()

# Return new error response.
def newError( text ) :
    return dump( { "error" : text } )

# Return new response.
def newResponse( obj ) :
    return dump( { "response": obj} )

##### Function for Report class #####

# To create an hash from target value.
def newUserHash( target ) :
    seed = ''
    keys = [
        'name',
        'screen_name',
        'description',
        'url',
        'followers_count',
        'friends_count',
        'favourites_count',
        'statuses_count',
        'profile_image_url',
        'profile_background_image_url'
    ]
    for key in range( len( keys ) ) :
        seed = seed + str( target[keys[key]] )
    return newHash( seed )

# Checking if the user exist in information table on user database.
def checkUser( name ) :
    userdb = db( 'user' )
    if not name :
        return newError( 'Invalid parameter of name' )
    result = userdb.db_result( 'select * from information where name="' + name + '"' )
    flag   = False
    if len( result ) :
        flag = True
    userdb.db_close()
    return newResponse( { "exist": flag } )

##### Class #####


# Initialize connection
# class initialize( object ) :
# 
#     def on_get( self, request, response ) :
#         print( "Reconnect database" )
#         userdb.db_close()
#         historydb.db_close()
#         profiledb.db_close()
#         tweetdb.db_close()
#         userdb    = db( 'user' )
#         historydb = db( 'history' )
#         profiledb = db( 'profile' )
#         tweetdb   = db( 'tweet' )
#         response.body = newResponse( 'Completed initialize' )
#
#     def on_post( self, request, response ) :
#        response.body = newError( 'Invalid request' )


# This class is insert information and update information.
class report( object ) :

    # Non use this method.
    def on_get( self, request, response ) :
        response.body = newError( 'Invalid request' )

    def on_post( self, request, response ) :
        body   = request.stream.read().decode( 'utf-8' )
        posted = json.loads( body )
        
        userdb    = db( 'user' )
        historydb = db( 'history' )
        profiledb = db( 'profile' )
        tweetdb   = db( 'tweet' )
        
        # Report identifier.
        postedIdentifier = newHash( body )

        if 'statuses' in posted and 'user' in posted :

            # User auth.
            auth = userdb.db_result( 'select accesstoken from information where name="' + posted['user']['name'] + '"' )

            # Registered user. Continue processing.
            if len( auth ) == 1 and auth[0]['accesstoken'] == posted['user']['access_token'] :

                # Checking if identifier exist in report table on history database.
                dbIdentifier = historydb.db_result( 'select * from report where hash="' + postedIdentifier + '"' )

                # This is new report. Continue processing.
                if len( dbIdentifier ) == 0 :

                    # Add history.
                    # id int auto_increment, name varchar( 255 ), comment text, os varchar( 255 ), pcuser varchar( 255 ), ip varchar( 255 ), date varchar( 255 ), macaddress varchar( 255 ), hash varchar( 255 ), index( id )
                    userData = posted['user']
                    historydb.db_insert( table='report', data={
                        "name"      : userData['name'],
                        "comment"   : userData['comment'],
                        "os"        : userData['os'],
                        "pcuser"    : userData['pcuser'],
                        "ip"        : request.host,
                        "date"      : now(),
                        "macaddress": userData['macaddress'],
                        "hash"      : postedIdentifier
                    } )

                    # Create new folder if not exist today folder.
                    path = checkAndNew()
                    newFile( join( 'files', path[0], path[1], path[2], postedIdentifier ), body )

                    # Shortcut statuses.
                    statuses = posted['statuses']

                    ##### Profile

                    
                    # No error here
                    
                    
                    
                    # Get profile list in profile database.
                    profileList = profiledb.db_result( 'show tables' )
                    for i in range( len( profileList ) ) :
                        profileList[i] = profileList[i]['Tables_in_profile']

                    # Profile : Main loop
                    for i in range( len( statuses ) ) :
                        target     = statuses[i]['user']
                        tableName  = 'id' + str( target['id'] )
                        targetHash = newUserHash( target )
                        
                        print( "--------------" )
                        print( tableName in profileList )
                        print( tableName )
                        print( profileList )

                        if not ( tableName in profileList ) :
                            print( 'create table' )
                            print(profiledb.db_query( 'create table ' + tableName + '(count int auto_increment, created_at varchar(255), default_profile varchar(255), default_profile_image varchar(255), description text, favourites_count varchar(255), followers_count varchar(255), friends_count varchar(255), id varchar(255), lang varchar(255), listed_count varchar(255), location text, name text, profile_background_image_url text, profile_image_url text, screen_name text,statuses_count varchar(255), time_zone varchar(255), url varchar(255), utc_offset varchar(255), verified varchar(255), rank int, hash varchar(255), index(count)) DEFAULT CHARACTER SET utf8' ))
                            print( 'insert' )
                            print(target['default_profile'] )
                            print(profiledb.db_insert( table=tableName, data={
                                "created_at"                  : urllib.parse.quote( str( target['created_at'] ) ),
                                "default_profile"             : urllib.parse.quote( str( target['default_profile'] ) ),
                                "default_profile_image"       : urllib.parse.quote( str( target['default_profile_image'] ) ),
                                "favourites_count"            : urllib.parse.quote( str( target['favourites_count'] ) ),
                                "description"                 : urllib.parse.quote( str( target['description'] ) ),
                                "followers_count"             : urllib.parse.quote( str( target['followers_count'] ) ),
                                "friends_count"               : urllib.parse.quote( str( target['friends_count'] ) ),
                                "id"                          : urllib.parse.quote( str( target['id'] ) ),
                                "lang"                        : urllib.parse.quote( str( target['lang'] ) ),
                                "listed_count"                : urllib.parse.quote( str( target['listed_count'] ) ),
                                "location"                    : urllib.parse.quote( str( target['location'] ) ),
                                "name"                        : urllib.parse.quote( str( target['name'] ) ),
                                "profile_background_image_url": urllib.parse.quote( str( target['profile_background_image_url'] ) ),
                                "profile_image_url"           : urllib.parse.quote( str( target['profile_image_url'] ) ),
                                "screen_name"                 : urllib.parse.quote( str( target['screen_name'] ) ),
                                "statuses_count"              : urllib.parse.quote( str( target['statuses_count'] ) ),
                                "time_zone"                   : urllib.parse.quote( str( target['time_zone'] ) ),
                                "url"                         : urllib.parse.quote( str( target['url'] ) ),
                                "utc_offset"                  : urllib.parse.quote( str( target['utc_offset'] ) ),
                                "verified"                    : urllib.parse.quote( str( target['verified'] ) ),
                                "rank"                        : 0,
                                "hash"                        : targetHash
                            } ))
                            historydb.db_insert( table='rank', data={
                                "id"         : urllib.parse.quote( str( target['id'] ) ),
                                "screen_name": urllib.parse.quote( str( target['screen_name'] ) ),
                                "name"       : urllib.parse.quote( str( target['name'] ) ),
                                "rank"       : 0
                            } )

                        latest = profiledb.db_result( 'select * from ' + tableName + ' order by count desc limit 1' )

                        # This profile ( target ) is new profile. Insert into profile database.
                        if targetHash != latest[0]['hash'] :
                            profiledb.db_insert( table=tableName, data={
                                "created_at"                  : urllib.parse.quote( str( target['created_at'] ) ),
                                "default_profile"             : urllib.parse.quote( str( target['default_profile'] ) ),
                                "default_profile_image"       : urllib.parse.quote( str( target['default_profile_image'] ) ),
                                "favourites_count"            : urllib.parse.quote( str( target['favourites_count'] ) ),
                                "description"                 : urllib.parse.quote( str( target['description'] ) ),
                                "followers_count"             : urllib.parse.quote( str( target['followers_count'] ) ),
                                "friends_count"               : urllib.parse.quote( str( target['friends_count'] ) ),
                                "id"                          : urllib.parse.quote( str( target['id'] ) ),
                                "lang"                        : urllib.parse.quote( str( target['lang'] ) ),
                                "listed_count"                : urllib.parse.quote( str( target['listed_count'] ) ),
                                "location"                    : urllib.parse.quote( str( target['location'] ) ),
                                "name"                        : urllib.parse.quote( str( target['name'] ) ),
                                "profile_background_image_url": urllib.parse.quote( str( target['profile_background_image_url'] ) ),
                                "profile_image_url"           : urllib.parse.quote( str( target['profile_image_url'] ) ),
                                "screen_name"                 : urllib.parse.quote( str( target['screen_name'] ) ),
                                "statuses_count"              : urllib.parse.quote( str( target['statuses_count'] ) ),
                                "time_zone"                   : urllib.parse.quote( str( target['time_zone'] ) ),
                                "url"                         : urllib.parse.quote( str( target['url'] ) ),
                                "utc_offset"                  : urllib.parse.quote( str( target['utc_offset'] ) ),
                                "verified"                    : urllib.parse.quote( str( target['verified'] ) ),
                                "rank"                        : latest[0]['rank'],
                                "hash"                        : targetHash
                            } )
                            historydb.db_update( table='rank', value={
                                "name"       : urllib.parse.quote( str( target['name'] ) ),
                                "screen_name": urllib.parse.quote( str( target['screen_name'] ) )
                            }, where={
                                "id": urllib.parse.quote( str( target['id'] ) )
                            } )

                    ##### Tweet

                    # Get tweet list in tweet database.
                    tweetList = tweetdb.db_result( 'show tables' )
                    for i in range( len( tweetList ) ) :
                        tweetList[i] = tweetList[i]['Tables_in_tweet']

                    # Tweet : Main loop
                    for i in range( len( statuses ) ) :
                        target    = statuses[i]
                        tableName = 'id' + str( target['user']['id'] )

                        if not ( tableName in tweetList ) :
                            tweetdb.db_query( 'create table ' + tableName + '(retweet_count varchar(255),favorite_count varchar(255),in_reply_to_user_id varchar(255),in_reply_to_status_id varchar(255),text varchar(255),id varchar(255) primary key,created_at varchar(255),iso_language_code varchar(255),source varchar(255),lang varchar(255),good int,bad int,index(id)) DEFAULT CHARACTER SET utf8' )

                        tweetId    = target['id']
                        existTweet = tweetdb.db_result( 'select id, good, bad from ' + tableName + ' where id="' + str( tweetId ) + '"' )

                        # Tweet is exist.
                        if len( existTweet ) > 0 :

                            existTweet = existTweet[0]

                            existTweetGood = existTweet['good']
                            existTweetBad = existTweet['bad']

                            # It does not match any value.
                            flag = 2

                            # Save tweet status.
                            if existTweetGood > existTweetBad :
                                flag = 0
                            elif existTweetGood == existTweetBad :
                                flag = 1

                            # Update value.
                            if target['flg'] == 'safe' :
                                existTweetGood = existTweetGood + 1
                            elif target['flg'] == 'none' :
                                existTweetBad  = existTweetBad + 1

                            # Performing a variation of rank.
                            if flag == 0 :
                                if existTweetGood == existTweetBad :
                                    profile = profiledb.db_result( 'select * from ' + tableName + ' order by count desc limit 1' )[0]
                                    profile['rank'] = profile['rank'] + 1

                                    # profile をそのまま挿入すると count カラムが自動でインクリメントされない
                                    # そのため最新のプロフィールが取れなくなる
                                    # count 3 ~ rank 0
                                    # count 3 ~ rank 1
                                    # count 3 ~ rank 1
                                    # がある場合一番上の count 3 ~ が取れる
                                    del profile['count']
                                    profiledb.db_insert( table=tableName, data=profile )
                                    print( 'good > bad -> good == bad' )
                                    historydb.db_update( table='rank', value={
                                        "rank": profile['rank']
                                    }, where={
                                        "id": urllib.parse.quote( str( target['user']['id'] ) )
                                    } )
                            elif flag == 1 :
                                if existTweetGood > existTweetBad :
                                    profile = profiledb.db_result( 'select * from ' + tableName + ' order by count desc limit 1' )[0]
                                    profile['rank'] = profile['rank'] - 1

                                    # profile をそのまま挿入すると count カラムが自動でインクリメントされない
                                    # そのため最新のプロフィールが取れなくなる
                                    # count 3 ~ rank 0
                                    # count 3 ~ rank 1
                                    # count 3 ~ rank 1
                                    # がある場合一番上の count 3 ~ が取れる
                                    del profile['count']
                                    profiledb.db_insert( table=tableName, data=profile )
                                    print( 'good == bad -> good > bad' )
                                    historydb.db_update( table='rank', value={
                                        "rank": profile['rank']
                                    }, where={
                                        "id": urllib.parse.quote( str( target['user']['id'] ) )
                                    } )

                            # Update tweet.
                            tweetdb.db_update( table=tableName, value={
                                "good": existTweetGood,
                                "bad" : existTweetBad
                            }, where={
                                "id": existTweet['id']
                            } )

                        # Tweet is not exist.
                        else :

                            good = 0
                            bad  = 0

                            if target['flg'] == 'safe' :
                                good = 1
                            elif target['flg'] == 'none' :
                                bad  = 1

                            tweetdb.db_insert( table=tableName, data={
                                "retweet_count"        : urllib.parse.quote( str( target['retweet_count'] ) ),
                                "favorite_count"       : urllib.parse.quote( str( target['favorite_count'] ) ),
                                "in_reply_to_user_id"  : urllib.parse.quote( str( target['in_reply_to_user_id'] ) ),
                                "in_reply_to_status_id": urllib.parse.quote( str( target['in_reply_to_status_id'] ) ),
                                "text"                 : urllib.parse.quote( str( target['text'] ) ),
                                "id"                   : urllib.parse.quote( str( target['id'] ) ),
                                "created_at"           : urllib.parse.quote( str( target['created_at'] ) ),
                                "iso_language_code"    : urllib.parse.quote( str( target['metadata']['iso_language_code'] ) ),
                                "source"               : urllib.parse.quote( str( target['source'] ) ),
                                "lang"                 : urllib.parse.quote( str( target['user']['lang'] ) ),
                                "good"                 : good,
                                "bad"                  : bad
                            } )

                            if bad == 1 :
                                profile = profiledb.db_result( 'select * from ' + tableName + ' order by count desc limit 1' )[0]
                                profile['rank'] = profile['rank'] + 1

                                # profile をそのまま挿入すると count カラムが自動でインクリメントされない
                                # そのため最新のプロフィールが取れなくなる
                                # count 3 ~ rank 0
                                # count 3 ~ rank 1
                                # count 3 ~ rank 1
                                # がある場合一番上の count 3 ~ が取れる
                                del profile['count']
                                profiledb.db_insert( table=tableName, data=profile )
                                print( 'good == bad -> good > bad' )
                                historydb.db_update( table='rank', value={
                                    "rank": profile['rank']
                                }, where={
                                    "id": urllib.parse.quote( str( target['user']['id'] ) )
                                } )

                # This report was already uploaded.
                else :
                    response.body = newError( 'Already uploaded' )

            # Incrrect user. Don't match accesstoken.
            else :
                response.body = newError( 'Invalid user' )

        # Incrrect data. haven't statuses or user key.
        else :
            response.body = newError( 'Incorrect data' )
        	
        userdb.db_close()
        historydb.db_close()
        profiledb.db_close()
        tweetdb.db_close()

# This class create new user or checking if the user in information table on user database.
# MySQL -> user -> information
# id varchar( 255 ), name varchar( 255 ), accesstoken varchar( 255 ), organization varchar( 255 ), date varchar( 255 ), index( id )
class user( object ) :

    def on_get( self, request, response ) :
        param  = request.get_param( 'name' )
        response.body = checkUser( param )

    def on_post( self, request, response ) :
        body   = request.stream.read()
        posted = json.loads( body.decode( 'utf-8' ) )
        	
        userdb = db('user')
        
        # Checking if value exist in object on posted data.
        if 'id' in posted and 'name' in posted and 'accesstoken' in posted and 'organization' in posted :
            flag = json.loads( checkUser( posted['name'] ) )

            # Error : Incorrect parameter of name
            if 'error' in flag :
                response.body = dump( flag )
                return
            # Error : The username is already in use
            if flag['response']['exist'] :
                response.body = newError( 'The username is already in use' )
                return

            # Insert into information table on user database.
            result = userdb.db_insert( table='information', data={
                "id"          : posted['id'],
                "name"        : posted['name'],
                "accesstoken" : posted['accesstoken'],
                "organization": posted['organization'],
                "date"        : now()
            } )
            response.body = newResponse( { "result": result } )
        else :
            response.body = newError( 'Invalid parameter' )
	
        userdb.db_close()


# This class have function that return list.
# MySQL -> history -> rank
# id varchar( 255 ), screen_name varchar( 255 ), name varchar( 255 ), rank int, index( rank )
class getList( object ) :

    def on_get( self, request, response ) :
        param = request.get_param( 'rank' )
        historydb = db( 'history' )
        if not re.match( '\d+', str( param ) ) :
            if param == 'others' :
                response.body = newResponse( historydb.db_result( 'select * from rank where rank>5' ) )
            else :
                response.body = newError( 'Invalid parameter of rank' )
            return
        data = historydb.db_result( 'select id, screen_name, name from rank where rank=' + param )
        for i in range( len( data ) ) :
            for j in data[i] :
                data[i][j] = urllib.parse.unquote( data[i][j] )
        response.body = newResponse( data )
        historydb.db_close()

    # Non use this method.
    def on_post( self, request, response ) :
        response.body = newError( 'Invalid request' )


##### Routing and Running #####

class route() :
    app = falcon.API()
    app.add_route( '/list', getList() )
    app.add_route( '/user', user() )
    app.add_route( '/report', report() )
#    app.add_route( '/', initialize() )

if __name__ == '__main__' :
    httpd = simple_server.make_server( host, port, route.app )
    httpd.serve_forever()
