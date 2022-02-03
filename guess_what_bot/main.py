import logging
import os
import re
import sys
from typing import Counter

import tweepy
from tweepy import api

from mention_bot import LastMentionService, MentionAction, MentionHandler

import encryption_util

game_opening = {
    'en': """@{username}
You've been challenged to a wordle!
It's a {length} characters word, can you guess it?
{data}
""",
    'he': """@{username}
אותגרת למשחק ניחושים!
זו מילה עם {length} אותיות, תוכל/י לנחש אותה?

{data}
"""
}

feedback_template = '''@{username} {feedback}

{data}'''

win_feedback_template = '@{username} {feedback}🥳'

huh_template = '@{username} 🤨'


encrypted_regex = re.compile(r'([a-zA-Z0-9_\-]{43,64}={0,2})')
mention_encrypted_regex = re.compile(r'@guess_what_bot\s+([a-zA-Z0-9_\-]{43,64}={0,2})')
guess_regex = re.compile(r'([a-zA-Z]+|[א-ת]+)')
en_word_regex = re.compile(r'^[a-z]{2,}$')
he_word_regex = re.compile(r'^[א-ת]{2,}$')


exact='🟩'
not_in_place = '🟨'
wrong = '⬜'

def parse_game_start_message(text):
    pass

def generate_feedback(word, guess):
    if word == guess:
        return '🟩'*len(word)
    if len(word) != len(guess):
        return None
    else:
        feedback = [None]*len(word)
        unmatched_counter = Counter(word)

        for i in range(len(guess)):
            if guess[i] == word[i]:
                feedback[i]=exact
                unmatched_counter[word[i]]-=1
        
        for i in range(len(guess)):
            if feedback[i] is None:
                if unmatched_counter[guess[i]]:
                    feedback[i] = not_in_place
                    unmatched_counter[guess[i]]-=1
                else:
                    feedback[i] = wrong

        print(feedback)
        return ''.join(feedback)

class MyLastMentionService(LastMentionService):
    def get_last_mention(self):
        return open(os.path.join(os.path.dirname(__file__),'mention.txt')).read()

    
    def set_last_mention(self, last_mention):
        open('mention.txt','w').write(last_mention)

class MyMentionAction(MentionAction):
    def __init__(self, api: tweepy.API) -> None:
        super().__init__()
        self.api = api

    def run(self, mention):
        if mention.in_reply_to_status_id is not None and \
                mention.in_reply_to_user_id == self.api.me().id:
            guess_groups = guess_regex.findall(mention.text)
            if guess_groups:
                guess = guess_groups[0].lower()
                game_status = self.api.get_status(id=mention.in_reply_to_status_id)
                game_groups = encrypted_regex.findall(game_status.text)
                if game_groups:
                    data = game_groups[0]
                    word, lang = encryption_util.decrypt(data)
                    if not en_word_regex.match(word) and not he_word_regex.match(word):
                        return
                    feedback = generate_feedback(word, guess)
                    if feedback is not None:
                        if word==guess:
                            status = win_feedback_template.format(username=mention.user.screen_name,
                                                            feedback=feedback)
                        else:
                            status = feedback_template.format(username=mention.user.screen_name,
                                                            feedback=feedback,
                                                            data=data)
                    else:
                        status = huh_template.format(username=mention.user.screen_name)
                    self.api.update_status(status=status,in_reply_to_status_id=mention.id)
        else:
            groups = mention_encrypted_regex.findall(mention.text)
            if groups:
                data = groups[0]
                word, lang = encryption_util.decrypt(data)
                status = game_opening[lang].format(username=mention.user.screen_name,
                                                    length=len(word),
                                                    data = data)
                self.api.update_status(status=status, in_reply_to_status_id=mention.id)
                
if __name__ == '__main__':
    log_modules = ['guess_what_bot', 'mention_bot']
    logFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logFormat)

    for module_name in log_modules:
        logger = logging.getLogger(module_name)
        logger.setLevel('DEBUG')
        logger.addHandler(console_handler)

    auth = tweepy.OAuthHandler(os.environ['TWITTER_CONSUMER_KEY'], os.environ['TWITTER_CONSUMER_SECRET'])
    auth.set_access_token(os.environ['TWITTER_ACCESS_TOKEN'], os.environ['TWITTER_ACCESS_TOKEN_SECRET'])

    tweepy_api = tweepy.API(auth, wait_on_rate_limit=True)
    is_production = os.environ.get('IS_PRODUCTION', 'True') == 'True'

    action = MyMentionAction(tweepy_api)
    last_mention_service = MyLastMentionService()

    mention_handler = MentionHandler(tweepy_api,
                                     action,
                                     last_mention_service,
                                     is_production,
                                     int(os.environ.get('MENTION_PROCESS_TIMEOUT', 30)),
                                     int(os.environ.get('RETRY_COUNT', 3)))
    mention_handler.run()
