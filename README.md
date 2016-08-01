# Spotlight-Server

### Requirement
- Mac OS X El Capitan 10.11.5
- Python 3.5.1
  - falcon (1.0.0)
  - mysql-connector (2.1.3)
- MySQL 5.7.11 MySQL Community Server

### How to use
#### Install
```
$ git clone https://github.com/calmery/spotlight-server.git  
$ pip3 install falcon
```  

MySQL  
```
mysql> create database tweet;  
mysql> create database profile;  

mysql> create database user;  
mysql> use user;  
mysql> create table information (id varchar(255), name varchar(255), accesstoken varchar(255), organization varchar(255), date varchar(255), index(id)) DEFAULT CHARACTER SET utf8;  

mysql> create database history;   
mysql> use history;  
mysql> create table rank (id varchar(255), screen_name varchar(255), name varchar(255), rank int, index(rank)) DEFAULT CHARACTER SET utf8;  
mysql> create table report (id int auto_increment, name varchar(255), comment text, os varchar(255), pcuser varchar(255), ip varchar(255), date varchar(255), macaddress varchar(255), hash varchar(255), index(id)) DEFAULT CHARACTER SET utf8;  
```

#### Run
```
$ python3 spotlight-server.py ADDRESS PORT
```

#### Request
- [NodeJS v4.4.7 LTS](https://nodejs.org/en/)  
  - request 2.74.0

```javascript
var request = require( "request" )

var data = {
  statuses       : [...],
  user           : {...},
  search_metadata: {...}
}

request.post( {
    uri: 'http://127.0.0.1:3000/report',
    form: JSON.stringify( data ),
    json: false
}, function( err, res, body ){
    if( !err ) console.log( res, body )
    else console.log( err )
} )
```
### License
Copyright (C) 2016 patchworks  
This software is released under the [GPL-2.0](https://opensource.org/licenses/GPL-2.0) License.

### Author
patchworks
- [Marei Kikukawa](https://github.com/calmery)
- [Naoya Sugita](https://github.com/naoyasugita)
- [Keisuke Toyota](https://github.com/KeisukeToyota)
