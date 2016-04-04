#! /usr/bin/python3
# -*- coding: utf8 -*-
# file: youtube.py youtube search crawler

#windows , linux
#pip install --user package_name
#python3 -m pip install requests
#python3 -m pip install BeautifulSoup4
#windows terminal default encoding: cp950
#want to execute successfully
#> chcp 65001 --> change the termain encodeing to utf-8

#freebsd (NCTU) using python3.4
#python3.4 -m  ensurepip --user
#python3.4 -m pip install --user beautifulsoup4
#python3.4 -m pip install --user requests

import argparse
import requests
import re
from bs4 import BeautifulSoup, NavigableString
import datetime
import os.path
import json

from urllib.parse import *


def is_digit( str ):
    for  c in str:
        if( c.isdigit() or c == ',')  == False:
            return False
    return True

def shorten_url( long_url ):

    encode_url = quote_plus( long_url ) # will also change space to plus sign
    #print( encode_url )
    query_urlfit = "https://developer.url.fit/api/shorten?long_url={0}".format( encode_url )

    #print( query_urlfit )
    r = requests.get( query_urlfit )
    #r.encoding="utf-8"
    #print( r.encoding )
    respond = r.text
    #print( respond )
    try:
        jsondata = json.loads( respond  )
    except ValueError:
        return ""
    hashvalue = jsondata['url']

#print( hashvalue )
    urlfit = "https://url.fit/"+hashvalue
    return urlfit



def count_extent( url ):
    html = requests.get( url ).text
    soup = BeautifulSoup( html , "html.parser" )
    rating_scope  = soup.find("div" ,id="watch8-sentiment-actions")

    values=[]
    for tag in rating_scope.find_all("span" , "yt-uix-button-content"):
#        print(tag)
#        print("")
#print( tag.parent )
        if tag.parent.name == "button":
            values.append( tag.text)


    if len( values ) < 3  or ( not is_digit( values[0] )  ) or ( not is_digit(values[2]) )  :
        #print(values[0].isdigit())
        #print( values )
        values = ["None"] *3

    #like before press button
    #like after press button
    #dislike before press button
    #disloke after press button
    #print( values)
    return values[0] , values[2]




if __name__ == "__main__":


    parser = argparse.ArgumentParser("Youtube Search Crawler")
    parser.add_argument("-n" , help="number of search result. default is 5" , dest="number" , type=int, default=5 , metavar="N")
    parser.add_argument("-p" , type=int, default=1 ,help="page that you want to parse" ,dest="page", metavar="P")
    parser.add_argument("keyword" ,type=str)
    args = parser.parse_args()

    if args.number <= 0:
#parser.print_help()
        print("The number of search result should be positive number!")
        exit()


#    print(args.keyword)
    youtube_url = "https://www.youtube.com/results?search_query={0}&page={1}".format(args.keyword , args.page)
    r = requests.get(youtube_url)

    youtube_html = r.text
    soup = BeautifulSoup( youtube_html  , "html.parser")
#print("Search url: "+youtube_url )

    count = 0
    for idx , tag in  enumerate( soup.find_all("div" , {'class':'yt-lockup-content'}) , start=0 ) :
        if count  >= args.number:
            break

        if 'yt-lockup-channel' in tag.parent.get("class")  or 'yt-lockup-playlist' in tag.parent.parent.get("class") :
            #print("Not video \n")
            continue

        info_list = tag.find_all(dir="ltr") #get title and description

        #print video title
        title = info_list[0].text
        url = "https://www.youtube.com"+info_list[0]['href']
        short_url = shorten_url( url )
        if short_url != "" : #short url success
            print( title + " (" + short_url + ")" )
        else:
            print( title + " (" + url + ")" )

        #print( tag.parent.get("class"))
        #print( tag.parent.parent.get("class") )


        count += 1
        if len(info_list) >= 2 : # has description
            for match in info_list[1].find_all(True): # remove the tag inner the description scope
                match.replaceWithChildren()
            print( str( info_list[1].text.replace(u'\xa0', u' ') ) ) # remove the \x0a --> ? unicode
        else:
            print("")
        count_like , count_dislike = count_extent( url )

        print("Like: {0} ,Dislike: {1}".format( count_like , count_dislike)  )
        #print( "number of extract:" + str( len(info_list )  ))

        print("\n")
