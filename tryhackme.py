#!/usr/bin/env python3

import utils
from pprint import pprint


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

    """
      curl -s "https://tryhackme.com/api/server-time" | jq

      curl -s "https://tryhackme.com/api/usersRank/7h3rAm" | jq
      curl -s "https://tryhackme.com/api/all-completed-rooms/7h3rAm" | jq

      curl -s "https://tryhackme.com/api/get-badges" | jq
      curl -s "https://tryhackme.com/api/new-rooms" | jq

      curl -s "https://tryhackme.com/api/room/network/throwback" | jq

      curl -s "https://tryhackme.com/api/room/vulnversity" | jq
      curl -s "https://tryhackme.com/api/tasks/vulnversity" | jq
      curl -s "https://tryhackme.com/api/get-votes/vulnversity" | jq
      curl -s "https://tryhackme.com/api/video/get/vulnversity" | jq

    """

  def stats_global(self):
    # curl -s "https://tryhackme.com/api/getstats" | jq
    return self._get_http(endpoint="/getstats")

  def hacktivities(self):
    # curl -s "https://tryhackme.com/api/hacktivities" | jq
    return self._get_http(endpoint="/hacktivities")


if __name__ == "__main__":
  thm = TryHackMe()

  pprint(thm.hacktivities())


