import urllib
import requests
import praw
import time
import config
import re
import urljoin
from selenium import webdriver
import collections
import datetime

def is_summon_chain(post):
    if not post.is_root:
        parent_comment_id = post.parent_id
        parent_comment = r.get_info(thing_id=parent_comment_id)
        if parent_comment.author != None and str(
                parent_comment.author.name) == 'PM_ME_Granter':  # TODO put your bot username here
            return True
        else:
            return False
    else:
        return False


def comment_limit_reached(post):
    global submissioncount
    count_of_this = int(float(submissioncount[str(post.submission.id)]))
    if count_of_this > 4:  # TODO change the number accordingly. float("inf") for infinite (Caution!)
        return True
    else:
        return False


def is_already_done(post):
    done = False
    numofr = 0
    try:
        repliesarray = post.replies
        numofr = len(list(repliesarray))
    except:
        pass
    if numofr != 0:
        for repl in post.replies:
            if repl.author != None and repl.author.name == 'PM_ME_Granter':  # TODO put your bot username here
                done = True
                continue
    if done:
        return True
    else:
        return False


def post_reply(reply, post):
    global submissioncount
    try:
        a = post.reply(reply)
        submissioncount[str(post.submission.id)] += 1
        return True
    except Exception as e:
        print("REPLY FAILED: %s @ %s" % (e, post.subreddit))
        if str(e) == '403 Client Error: Forbidden':
            print('/r/' + post.subreddit + ' has banned me.')
            # save_changing_variables()
        return False

def get_images(soup):
    images = [img for img in soup.findAll('img')]
    print (str(len(images)) + " images found.")
    print('Downloading images to current working directory.')
    image_links = [each.get('src') for each in images]
    for each in image_links:
        print(each)
        try:
            filename = each.strip().split('/')[-1].strip()
            src = urljoin(url, each)
            print('Getting: ' + filename)
            response = requests.get(src, stream=True)
            # delay to avoid corrupted previews
            time.sleep(1)
            # with open(filename, 'wb') as out_file:
            #     shutil.copyfileobj(response.raw, out_file)
        except:
            print('  An error occured. Continuing.')
    print('Done.')


def get_search_terms(username):
    regex = re.compile('^(pm_me_).+', re.IGNORECASE)
    result = regex.search(username)
    if result == None:
        return []
    result = result.group(0)
    result = result.split("_")[2:] #cut pm_me
    result = " ".join(result)
    result = result.replace("_", " ")
    return result

def bot_login():
    r = praw.Reddit(username = config.username,
            password = config.password,
            client_id = config.client_id,
            client_secret = config.client_secret,
            user_agent = "PM Wish Granter")
    return r

def contains_PmMe(username):
    regex = re.compile('^(pm_me_).+', re.IGNORECASE)
    matches = regex.search(username)
    if matches != None:
        return
    return False

def make_query(terms):
    return urllib.parse.urlencode({'q': terms})

def run_bot(r):
    to_today = datetime.datetime.now().timestamp()
    from_yesterday = to_today - 24 * 60 * 60 * 60
    sub = r.subreddit("all").top("day")
    for submission in sub:
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            if comment.body == "!GrantPM":
                print("Found a Comment in " + submission.title)
                cm_parent = comment.parent()
                if cm_parent.author != None:
                    print("About to comment.")
                    terms = get_search_terms(cm_parent.author.name)
                    query = make_query(terms)
                    src = get_image_src("{0}{1}".format(BING, query))
                    content = "Your wish shall be granted! [Here]({0}) you find what you desire: {1}.".format(src, terms)
                    post_reply(content, cm_parent) #Doesn't comment if you already have
                    print("Comment succesful.")
        print("Done with comments in: " + submission.title)
    print("Done with sumbission stream.")

def get_image_src(url):
    WEBBROWSER.get(url)
    WEBBROWSER.find_element_by_id(BING_BUTTON_ID).click()
    time.sleep(1)
    detail_url = WEBBROWSER.find_elements_by_css_selector(".imgpt > a")
    result = detail_url[0].get_attribute("href")
    WEBBROWSER.get(result)
    time.sleep(1)
    div_tag = WEBBROWSER.find_element_by_id(FOCUS_ID)
    img_tag = div_tag.find_element_by_css_selector('img')
    time.sleep(1)
    return img_tag.get_attribute("src")

BING = "https://www.bing.com/images/search?"
BING_BUTTON_ID = "sb_form_go"
WEBBROWSER = webdriver.Chrome()
FOCUS_ID = "iol_imw"
r = bot_login()
submissioncount = collections.Counter()
while True:
    run_bot(r)