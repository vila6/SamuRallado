    # -*- coding: utf-8 -*-
import tweepy
import json
import re
import os
import string
from PIL import Image
import gc

from secrets import *
import imagesearch

auth = tweepy.OAuthHandler(C_KEY,C_SECRET)
auth.set_access_token(A_TOKEN,A_TOKEN_SECRET)
api = tweepy.API(auth)

stream_rule = " "
account_screen_name = "samurallado"
account_user_id = "658102"

def Oimage(image):
    background = Image.open("img/"+image)
    foreground = Image.open("img/samurallado.png")
    bw = background.size[0]
    bh = background.size[1]
    fw = foreground.size[0]
    fh = foreground.size[1]
    if bw < fw:
        resize = (int(bw*fw/bw),int(bh*fw/bw))
        background = background.resize(resize,Image.ANTIALIAS)
        bw = background.size[0]
        bh = background.size[1]
    if bh < fh:
        resize =  (int(bw*fh/bh),int(bh*fh/bh))
        background = background.resize(resize,Image.ANTIALIAS)
        bw = background.size[0]
        bh = background.size[1]
    background.paste(foreground, (bw-fw,bh-fh), foreground)
    background.save("output.png") 
    os.remove("img/"+image)
    background.close()
    foreground.close()  

def archive(text):
    file_txt = open('archives.txt','a')
    file_txt.write("\n"+text)
    file_txt.close()


def create_tweet(txt):
    txt = re.sub("samu ralado por ",'',txt)
    txt = re.sub("Samu rallado por ",'',txt)
    txt = re.sub("Samu Rallado por ",'',txt)
    txt = re.sub("Samu rallado por ",'',txt)
    txt = re.sub("Samu rallado por ",'',txt)
    txt = re.sub("Samu rallado por ",'',txt)
    txt = re.sub("Samu rallado por ",'',txt)
    txt = re.sub("Samu rallado por ",'',txt)
    img = imagesearch.image_search(txt)
    if img != False:
        try:
            Oimage(img)
        except OSError:
            img = False
        archive(txt)
    image_size = os.path.getsize("output.png")
    print(image_size)
    if image_size >= 3072000:
        print('File too big! Returning false')
        img = False

    return (txt,img)


class ReplyToTweet(tweepy.StreamListener):

    def on_data(self, data):
        print('Tweet received!')
        tweet = json.loads(data.strip())
        retweeted = tweet.get('retweeted')
        faved = tweet.get('favorited')
        if retweeted is not None and not retweeted and tweet.get('user',{}).get('id_str','') != account_user_id and tweet.get('user', {}).get('screen_name') != account_screen_name and 'retweeted_status' not in tweet:
            print(tweet.get('user', {}).get('id_str', ''))
            tweetId = tweet.get('id_str')
            screenName = tweet.get('user', {}).get('screen_name')
            
            tweetText = tweet.get('text').encode('utf-8')

            tweetText = tweetText.decode('ascii',errors='ignore')
            tweetText = re.sub('@samurallado','',tweetText)
            tweetText = re.sub('@SAMURALLADO','',tweetText)
            tweetText = re.sub('@Samurallado','',tweetText)
            tweetText = re.sub('@SamuRallado','',tweetText)
            tweetText = re.sub('#','',tweetText)

            full_reply = create_tweet(tweetText)
            if full_reply[1] == False:
                replyText = '@' + screenName + ' ' + "No he podido encontrar " + full_reply[0] + " intenta con otra cosa o algo"
                api.update_status(status=replyText, in_reply_to_status_id=tweetId)
                gc.collect()
            else:
                replyText = '@' + screenName + ' ' + "Samu rallado por" + full_reply[0]
                api.update_with_media("output.png",status=replyText, in_reply_to_status_id=tweetId)
                gc.collect()

    def on_error(self, status):
        print("ERROR #"+str(status))

tweetText = ''

if __name__ == "__main__":
    streamListener = ReplyToTweet()
    twitterStream = tweepy.Stream(auth, streamListener)
    twitterStream.userstream(_with='user')
