import urllib
import praw
import time
import config
import re
from selenium import webdriver
import collections

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
    global submissionCount
    try:
        a = post.reply(reply)
        submissionCount[str(post.submission.id)] += 1
        return True
    except Exception as e:
        print("REPLY FAILED: %s @ %s" % (e, post.subreddit))
        if str(e) == '403 Client Error: Forbidden':
            print('/r/' + post.subreddit + ' has banned me.')
            # save_changing_variables()
        return False

def clean_search_terms(terms):
    lower_terms = [t.lower() for t in terms]
    for ban_t in BAN_TERMS:
        if ban_t in lower_terms:
            lower_terms.remove(ban_t)
    return lower_terms

def get_search_terms(username):
    regex = re.compile('^(pm_me_).+', re.IGNORECASE)
    result = regex.search(username)
    if result is None:
        return []
    result = result.group(0)
    result = result.split("_")[2:] #cut pm_me
    result = clean_search_terms(result)
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
    if not matches is None:
        return True
    return False

def make_query(terms):
    return urllib.parse.urlencode({'q': terms})

def check_all_comments(comments):
    comments.replace_more(limit=0)
    for comment in comments:
        if len(comment.replies) > 0:
            check_all_comments(comment.replies)
        else:
            attempt_to_reply(comment)

def attempt_to_reply(comment):
    if comment.body == "!GrantPM":
        print("Found a Comment!")
        cm_parent = comment.parent()
        if can_reply(comment):
            print("About to comment.")
            terms = get_search_terms(cm_parent.author.name)
            query = make_query(terms)
            src = get_image_src("{0}{1}".format(BING, query))
            if src is None:
                print("No pic found for terms: " + terms)
                return
            content = build_reply_string(src, terms)
            post_reply(content, comment)
            authors.append(comment.author.name)
            print("Comment successful.")
        else:
            print("Could not reply.")

def can_reply(comment):
    if not comment.author is None:
        author_name = comment.author.name
        if author_name == "PM_ME_Granter":
            return False
        return (not author_name in authors) and contains_PmMe(comment.author.name) and not already_replied(comment)
    return False

def build_reply_string(src, terms):
    return "Your wish shall be granted! [Here]({0}) you find what you desire: {1}.\nI'm a bot and still in development.".format(src, terms)

def run_bot(r):
    sub = r.subreddit("testabot").new()
    for submission in sub:
        submission.comments.replace_more(limit=0)
        check_all_comments(submission.comments)
        for comment in submission.comments.list():
            attempt_to_reply(comment)
        print("Done checking comments in post: " + submission.title)
    print("Done with submission stream.")

def already_replied(comment):
    for child in comment.replies:
        if (not child.author is None) and child.author.name == "PM_ME_Granter":
            return True
    return False

def get_image_src(url):
    WEBBROWSER.get(url)
    WEBBROWSER.find_element_by_id(BING_BUTTON_ID).click()
    time.sleep(2)
    detail_url = WEBBROWSER.find_elements_by_css_selector(".imgpt > a")
    try:
        result = detail_url[0].get_attribute("href")
    except Exception:
        return None
    WEBBROWSER.get(result)
    time.sleep(2)
    div_tag = WEBBROWSER.find_element_by_id(FOCUS_ID)
    img_tag = div_tag.find_element_by_css_selector('img')
    return img_tag.get_attribute("src")

BAN_TERMS = ["your", "ur", "pic", "pics", "pix", "dick", "nude", "nudes", "tit", "tits"]
BING = "https://www.bing.com/images/search?"
BING_BUTTON_ID = "sb_form_go"
WEBBROWSER = webdriver.Chrome()
FOCUS_ID = "mainImageWindow"
r = bot_login()
submissionCount = collections.Counter()
authors = []
# while True:
run_bot(r)
