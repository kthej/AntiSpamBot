import sys
sys.path.insert(0, 'vendor')

import os
import requests
import random
import json


API_ROOT = 'https://api.groupme.com/v3/'
FLAGGED_PHRASES = (
    
    "selling roc pass",
    "selling my roc pass",
    "selling the roc pass",
    "selling a roc pass",
    "selling roc passes",
    "sell roc pass",
    "roc pass for sale",
    "roc passes for sale",
    "roc pass available",
    "selling my roc",
    "selling roc",
    "roc pass"
)


def get_memberships(group_id, token):
    response = requests.get(f'{API_ROOT}groups/{group_id}', params={'token': token}).json()['response']['members']
    return response

def get_membership_id(group_id, user_id, token):
    memberships = get_memberships(group_id, token)
    for membership in memberships:
        if membership['user_id'] == user_id:
            return membership['id']
    return None

def remove_member(group_id, membership_id, token):
    response = requests.post(f'{API_ROOT}groups/{group_id}/members/{membership_id}/remove', params={'token': token})
    print('Attempted to kick user, got response:')
    print(response.text)
    return response.ok  # Return whether the request was successful


def delete_message(group_id, message_id, token):
    response = requests.delete(f'{API_ROOT}conversations/{group_id}/messages/{message_id}', params={'token': token})
    return response.ok


def kick_user(group_id, user_id, token):
    membership_id = get_membership_id(group_id, user_id, token)
    if membership_id:
        return remove_member(group_id, membership_id, token)
    return False




def receive(event, context):
    message = json.loads(event['body'])
    bot_id = message['bot_id']

    for phrase in FLAGGED_PHRASES:
        if phrase in message['text'].lower():
            # Attempt to kick the user and check if it was successful
            if kick_user(message['group_id'], message['user_id'], message['token']):
                delete_message(message['group_id'], message['id'], message['token'])
                send('Kicked ' + message['name'] + ' due to apparent spam post.', bot_id)
            else:
                print('Kick attempt failed or user is an admin.')
            break

    return {
        'statusCode': 200,
        'body': 'ok'
    }


def send(text, bot_id):
    url = 'https://api.groupme.com/v3/bots/post'

    message = {
        'bot_id': bot_id,
        'text': text,
    }
    r = requests.post(url, json=message)
