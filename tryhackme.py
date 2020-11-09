#!/usr/bin/env python3

import utils


class TryHackMe:
  """
    open endpoints:
    curl -s "https://tryhackme.com/api/all-completed-rooms/7h3rAm" | jq
    curl -s "https://tryhackme.com/api/get-badges" | jq
    curl -s "https://tryhackme.com/api/get-votes/vulnversity" | jq
    curl -s "https://tryhackme.com/api/getstats" | jq
    curl -s "https://tryhackme.com/api/hacktivities" | jq
    curl -s "https://tryhackme.com/api/new-rooms" | jq
    curl -s "https://tryhackme.com/api/room/network/throwback" | jq
    curl -s "https://tryhackme.com/api/room/vulnversity" | jq
    curl -s "https://tryhackme.com/api/server-time" | jq
    curl -s "https://tryhackme.com/api/tasks/vulnversity" | jq
    curl -s "https://tryhackme.com/api/usersRank/7h3rAm" | jq
    curl -s "https://tryhackme.com/api/video/get/vulnversity" | jq

    authenticated endpoints:
    curl -s "https://tryhackme.com/account/subscription-cost" | jq
    curl -s "https://tryhackme.com/api/check-verification" | jq
    curl -s "https://tryhackme.com/api/get-my-votes/vulnversity" | jq
    curl -s "https://tryhackme.com/api/myrooms" | jq
    curl -s "https://tryhackme.com/api/questions-answered" | jq
    curl -s "https://tryhackme.com/api/room-percentages" | jq
    curl -s "https://tryhackme.com/api/running-instances" | jq
    curl -s "https://tryhackme.com/api/tutorial-status" | jq
    curl -s "https://tryhackme.com/get-path/beginner" | jq
    curl -s "https://tryhackme.com/message/get-unseen" | jq
    curl -s "https://tryhackme.com/notifications/get" | jq
    curl -s "https://tryhackme.com/notifications/get" | jq
    curl -s "https://tryhackme.com/recommend/dash" | jq
  """

  def __init__(self):
    self.version = "0.1"
    self.baseurl = "https://tryhackme.com/api"
    self.useragent = "Python THM Client/%s" % (self.version)
    self.headers = { "User-Agent": self.useragent }

  def _get_http(self, endpoint):
    self.headers["Content-Type"] = "application/json;charset=utf-8"
    url = "%s/%s" % (self.baseurl, endpoint)
    return utils.get_http(url=url, headers=self.headers)

  def _post_http(self, endpoint, data):
    self.headers["Content-Type"] = "application/json;charset=utf-8"
    url = "%s/%s" % (self.baseurl, endpoint)
    return utils.post_http(url, data, self.headers)

  def stats_global(self):
    # curl -s "https://tryhackme.com/api/getstats" | jq
    return self._get_http(endpoint="/getstats")

  def rooms(self): ## get details for all walkthroughs and challenges
    # curl -s "https://tryhackme.com/api/hacktivities" | jq
    return self._get_http(endpoint="/hacktivities")

  def room_details(self, room, verbose=False):
    # curl -s "https://tryhackme.com/api/room/vulnversity" | jq
    # curl -s "https://tryhackme.com/api/tasks/vulnversity" | jq
    # curl -s "https://tryhackme.com/api/get-votes/vulnversity" | jq
    # curl -s "https://tryhackme.com/api/video/get/vulnversity" | jq
    room = self._get_http(endpoint="/room/%s" % (room))
    if verbose and room:
      room["tasks"] = self._get_http(endpoint="/tasks/%s" % (room))
      room["votes"] = self._get_http(endpoint="/get-votes/%s" % (room))
      room["videos"] = self._get_http(endpoint="/video/get/%s" % (room))
    return room
