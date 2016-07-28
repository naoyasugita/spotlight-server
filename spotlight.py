# -*- coding: utf-8 -*-

import os
import json
import datetime
import sys
import hashlib

from wsgiref import simple_server

# Import a module from a relative path.
sys.path.append( './library' )

import falcon
import mysql_connector_wrapper as mcw

# Command line arguments
# The first argument is host and second argument is port number.
param = sys.argv

host  = str( param[1] )
port  = int( param[2] )

# Databases
userdb  = mcw.MySQLConnect( user='root', passwd='pass', charset='utf8', db='user' )
histdb  = mcw.MySQLConnect( user='root', passwd='pass', charset='utf8', db='hist' )
datadb  = mcw.MySQLConnect( user='root', passwd='pass', charset='utf8', db='data' )
tweetdb = mcw.MySQLConnect( user='root', passwd='pass', charset='utf8', db='tweet' )
userdb  = mcw.MySQLConnect( user='root', passwd='pass', charset='utf8', db='user' )
rankdb  = mcw.MySQLConnect( user='root', passwd='pass', charset='utf8', db='rank' )

# Function

c = os.path.exists
p = os.path.join

# Returns current time.
def now( option='%Y%m%d%H%M%S' ) :
    return datetime.datetime.now().strftime( option )

# Check and create new folder.
def checkAndCreate() :
    base  = 'files'
    year  = now( '%y' )
    month = now( '%m' )
    day   = now( '%d' )
    
    try :
        if not c( p( base, year ) ) :
            os.mkdir( p( base, year ) )
            os.mkdir( p( base, year, month ) )
            os.mkdir( p( base, year, month, day ) )
        else :
            if not c( p( base, year, month ) ) :
                os.mkdir( p( base, year, month ) )
                os.mkdir( p( base, year, month, day ) )
            else :
                if not c( p( base, year, month, day ) ) :
                    os.mkdir( p( base, year, month, day ) )
        return [ year, month, day ]
    except :
        return False

def createBackupFile( filename, text ) :
    try :
        f = open( filename, 'w' )
        f.write( text )
        f.close()
        return True
    except :
        return False

def createHash( text ) :
    return hashlib.sha224( text.encode('utf-8') ).hexdigest()

def createUserHash( target ) :
    obj = ['name', 'screen_name', 'description', 'url', 'followers_count', 'friends_count', 'favourites_count', 'statuses_count', 'profile_image_url', 'profile_background_image_url']
    output = ''
    for i in range( len( obj ) ) :
        output = output + str( target[obj[i]] )
    return createHash( output )

# class

class report( object ):
    
    def on_post( self, request, response ) :
        body = request.stream.read().decode( 'utf-8' )
        data = json.loads( body )
        dataHash = createHash( body )
        
        if 'statuses' in data and 'user' in data :
            
            authdb = userdb.db_result( 'select accesstoken from auth where userid="' + data['user']['userid'] + '";' )
            
            if authdb[0]['accesstoken'] == data['user']['access_token'] :
                
                
                checkExsist = histdb.db_result( 'select * from report where hash="' + dataHash + '";' )
                if len( checkExsist ) == 0 :
                    
                    histdb.db_insert( table='report', data={
                        "comment": data['user']['comment'],
                        "name"   : data['user']['userid'],
                        "os"     : data['user']['os'],
                        "pcuser" : data['user']['pcuser'],
                        "mac"    : data['user']['macadress'],
                        "ip"     : request.host,
                        "date"   : now(),
                        "hash"   : dataHash
                    })
                    
                    # Upload json file.
                    path = checkAndCreate()
                    createBackupFile( p( 'files', path[0], path[1], path[2], dataHash ), body )
                    
                    # Shortcut
                    statuses = data['statuses']
                    
                    # Get table list in data database.
                    profileList = datadb.db_result( 'show tables' )
                    for i in range( len( profileList ) ) :
                        profileList[i] = profileList[i]['Tables_in_data']
                    
                    for i in range( len( statuses ) ) :
                        target = statuses[i]['user']
                        tableName = 'id' + str( target['id'] )
                        if not ( tableName in profileList ) :
                            datadb.db_query( 'create table ' + tableName + '(count int auto_increment, created_at varchar(255), default_profile varchar(255), default_profile_image varchar(255), description varchar(255), favourites_count varchar(255), followers_count varchar(255), friends_count varchar(255), id varchar(255), lang varchar(255), listed_count varchar(255), location varchar(255), name varchar(255), profile_background_image_url varchar(255), profile_image_url varchar(255), screen_name varchar(255),statuses_count varchar(255), time_zone varchar(255), url varchar(255), utc_offset varchar(255), verified varchar(255), rank int, hash varchar(255), index(count)) DEFAULT CHARACTER SET utf8' )
                        nowHash = createUserHash( target )
                        latest = datadb.db_result( 'select hash from ' + tableName + ' order by count desc limit 1' )
                        if len( latest ) == 0 or not ( nowHash == latest[0]['hash'] ) :
                            datadb.db_insert( table=tableName, data={
                                "created_at"                  : str( target['created_at'] ),
                                "default_profile"             : str( target['default_profile'] ),
                                "default_profile_image"       : str( target['default_profile_image'] ),
                                "favourites_count"            : str( target['favourites_count'] ),
                                "description"                 : str( target['description'] ),
                                "followers_count"             : str( target['followers_count'] ),
                                "friends_count"               : str( target['friends_count'] ),
                                "id"                          : str( target['id'] ),
                                "lang"                        : str( target['lang'] ),
                                "listed_count"                : str( target['listed_count'] ),
                                "location"                    : str( target['location'] ),
                                "name"                        : str( target['name'] ),
                                "profile_background_image_url": str( target['profile_background_image_url'] ),
                                "profile_image_url"           : str( target['profile_image_url'] ),
                                "screen_name"                 : str( target['screen_name'] ),
                                "statuses_count"              : str( target['statuses_count'] ),
                                "time_zone"                   : str( target['time_zone'] ),
                                "url"                         : str( target['url'] ),
                                "utc_offset"                  : str( target['utc_offset'] ),
                                "verified"                    : str( target['verified'] ),
                                "rank"                        : 0,
                                "hash"                        : nowHash
                            } )
                        
                    # Tweets
                    tweetList = tweetdb.db_result( 'show tables' )
                    for i in range( len( tweetList ) ) :
                        tweetList[i] = tweetList[i]['Tables_in_tweet']
                    
                    for i in range( len( statuses ) ) :
                        target = statuses[i]
                        tableName = 'id' + str( target['user']['id'] )
                        if not ( tableName in tweetList ) :
                            tweetdb.db_query( 'create table ' + tableName + '(retweet_count varchar(255),favorite_count varchar(255),in_reply_to_user_id varchar(255),in_reply_to_status_id varchar(255),text varchar(255),id varchar(255) primary key,created_at varchar(255),iso_language_code varchar(255),source varchar(255), lang varchar(255),good int,bad int,index(id)) DEFAULT CHARACTER SET utf8' )
                        nowId  = target['id']
                        latest = tweetdb.db_result( 'select id, good, bad from ' + tableName + ' where id="' + str( nowId ) + '"' )
                        
                        # Exsist
                        if len( latest ) > 0 :
                            
                            latest = latest[0]
                            
                            good = latest['good']
                            bad  = latest['bad']
                            
                            if good > bad :
                                flg = 0
                            else :
                                flg = 1
                            
                            if target['flg'] == 'safe' :
                                good = good + 1
                            elif target['flg'] == 'none' :
                                bad  = bad + 1
                            
                            tweetdb.db_update( table=tableName, value={
                                "good": good,
                                "bad" : bad
                            }, where={
                                "id": nowId
                            } )
                            
                            profile = datadb.db_result( 'select * from ' + tableName + ' order by count desc limit 1' )
                            profile = profile[0]
                            
                            print( profile['rank'] )
                            
                            if flg == 0 :
                                # rank up
                                if bad >= good :
                                    profile['rank'] = profile['rank'] + 1
                                    datadb.db_insert( table=tableName, data=profile )
                            elif flg == 1 :
                                # rank down
                                if good > bad :
                                    if profile['rank'] > 0 :
                                        profile['rank'] = profile['rank'] - 1
                                        datadb.db_insert( table=tableName, data=profile )
                                        
                        # Not exsist
                        else :
                            
                            good = 0
                            bad  = 0
                            if target['flg'] == 'safe' :
                                good = 1
                            elif target['flg'] == 'none' :
                                bad  = 1
                            tweetdb.db_insert( table=tableName, data={
                                "retweet_count"        : str( target['retweet_count'] ),
                                "favorite_count"       : str( target['favorite_count'] ),
                                "in_reply_to_user_id"  : str( target['in_reply_to_user_id'] ),
                                "in_reply_to_status_id": str( target['in_reply_to_status_id'] ),
                                "text"                 : str( target['text'] ),
                                "id"                   : str( target['id'] ),
                                "created_at"           : str( target['created_at'] ),
                                "iso_language_code"    : str( target['metadata']['iso_language_code'] ),
                                "source"               : str( target['source'] ),
                                "lang"                 : str( target['user']['lang'] ),
                                "good"                 : good,
                                "bad"                  : bad
                            } )
                            profile = datadb.db_result( 'select * from ' + tableName + ' order by count desc limit 1' )
                            profile = profile[0]
                            add = 0
                            if bad == 1 :
                                add = 1
                            else :
                                if profile['rank'] > 0 :
                                    add = -1
                            profile['rank'] = profile['rank'] + add
                            if not ( add == 0 ) :
                                datadb.db_insert( table=tableName, data=profile )
                        
                # Already uploaded
                else :
                    response.body = json.dumps( { "error": "Already uploaded" } )
                
            # Incorrect user
            else : 
                response.body = json.dumps( { "error": "Incorrect user" } )
        
        # Incorrect data
        else :
            response.body = json.dumps( { "error": "Incorrect data" } )

# Create new user.
class user( object ) :
    
    def on_post( self, request, response ) : 
        body = request.stream.read()
        data = json.loads( body.decode( 'utf-8' ) )
        print("now")
        if data['userid'] and data['username'] and data['accesstoken'] and data['organization'] :
            result  = userdb.db_result( "select id from user where username='" + data['username'] + "'" )
            flg     = False
            if len( result ) == 0 :
                result = userdb.db_insert( table='user', data={
                    "userid"      : data['userid'],
                    "username"    : data['username'],
                    "accesstoken" : data['accesstoken'],
                    "organization": data['organization'],
                    "date"        : now()
                } )
                response.body = json.dumps( { "result": True } )
            else :
                response.body = json.dumps( { "error": "Already exsist" } )
        else :
            response.body = json.dumps( { "error": "Incorrect parameter or value"  } )
        
    def on_get( self, request, response ) :
        param   = request.get_param( 'name' )
        print( param )
        result  = userdb.db_result( "select id from user where username='" + param + "'" )
        flg     = False
        if len( result ) :
            flg = True
        response.body = json.dumps( { "exsist": flg } )

# Routing

class route() :
    app = falcon.API()
    app.add_route( '/report', report() )
    app.add_route( '/user', user() )

# Runnning

if __name__ == '__main__' :
    httpd = simple_server.make_server( host, port, route.app )
    httpd.serve_forever()