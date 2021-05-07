#!/usr/bin/env python3

import utils


class TryHackMe:
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
    return self._get_http(endpoint="/hacktivities?limit=1000")

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

  def stats_global(self):
    # curl -s "https://tryhackme.com/api/getstats" | jq
    return self._get_http(endpoint="/getstats")
