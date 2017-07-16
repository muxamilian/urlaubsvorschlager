#!/usr/bin/python
# coding: utf-8

import facebook
import os 

oauth_access_token = os.environ.get('FB_USER_TOKEN')

facebook_graph = facebook.GraphAPI(oauth_access_token)
print(facebook_graph.get_object('me/tagged_places'))