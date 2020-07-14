#!/usr/bin/env python3

import utils


class HackTheBox:
  def __init__(self, apikey):
    self.version = "0.1"
    self.apikey = apikey
    self.baseurl = "https://www.hackthebox.eu/api"
    self.useragent = "Python HTB Client/%s" % (self.version)
    self.headers = { "User-Agent": self.useragent }

  def _get_http(self, endpoint, authorize=False):
    self.headers["Content-Type"] = "application/json;charset=utf-8"
    if authorize:
      self.headers["Authorization"] = "Bearer %s" % (self.apikey)
    url = "%s/%s" % (self.baseurl, endpoint)
    return utils.get_http(url, self.headers)

  def _post_http(self, endpoint, data, authorize=False):
    self.headers["Content-Type"] = "application/json;charset=utf-8"
    if authorize:
      self.headers["Authorization"] = "Bearer %s" % (self.apikey)
    url = "%s/%s" % (self.baseurl, endpoint)
    return utils.post_http(url, data, self.headers)

  def stats_overview(self):
    # curl -s 'https://www.hackthebox.eu/api/stats/overview' | jq .
    return self._get_http(endpoint="/stats/overview", authorize=False)

  def stats_global(self):
    # curl -s 'https://www.hackthebox.eu/api/stats/global' --data '' | jq .
    return self._post_http(endpoint="/stats/global", data={}, authorize=False)

  def stats_daily_owns(self, mid):
    # curl -s 'https://www.hackthebox.eu/api/stats/daily/owns/1' --data '' | jq .
    return self._post_http(endpoint="/stats/daily/owns/%d" % (mid), data={}, authorize=False)

  def machines_get_matrix(self, mid):
    # curl -s 'https://www.hackthebox.eu/api/machines/get/matrix/1' -H 'Authorization: Bearer <apikey>' | jq .
    return self._get_http(endpoint="/machines/get/matrix/%d" % (mid), authorize=True)

  def machines_get_all(self):
    # curl -s 'https://www.hackthebox.eu/api/machines/get/all' -H 'Authorization: Bearer <apikey>' | jq .
    return self._get_http(endpoint="/machines/get/all", authorize=True)

  def machines_get(self, mid):
    # curl -s 'https://www.hackthebox.eu/api/machines/get/253' -H 'Authorization: Bearer <apikey>' | jq .
    return self._get_http(endpoint="/machines/get/%d" % (mid), authorize=True)

  def machines_difficulty(self):
    # curl -s 'https://www.hackthebox.eu/api/machines/difficulty' -H 'Authorization: Bearer <apikey>' | jq .
    return self._get_http(endpoint="/machines/difficulty", authorize=True)

  def machines_terminating(self):
    # curl -s 'https://www.hackthebox.eu/api/machines/terminating' -H 'Authorization: Bearer <apikey>' | jq .
    return self._get_http(endpoint="/machines/terminating", authorize=True)

  def machines_resetting(self):
    # curl -s 'https://www.hackthebox.eu/api/machines/resetting' -H 'Authorization: Bearer <apikey>' | jq .
    return self._get_http(endpoint="/machines/resetting", authorize=True)

  def machines_expiry(self):
    # curl -s 'https://www.hackthebox.eu/api/machines/expiry' -H 'Authorization: Bearer <apikey>' | jq .
    return self._get_http(endpoint="/machines/expiry", authorize=True)

  def vpnserver_freeslots(self):
    # curl -s 'https://www.hackthebox.eu/api/vpnserver/freeslots' -H 'Authorization: Bearer <apikey>' -H 'Content-Type: application/json;charset=utf-8' --data '' | jq .
    return self._post_http(endpoint="/vpnserver/freeslots", data={}, authorize=True)

  def vpnserver_status_all(self):
    # curl -s 'https://www.hackthebox.eu/api/vpnserver/status/all' -H 'Authorization: Bearer <apikey>' | jq .
    return self._get_http(endpoint="/vpnserver/status/all", authorize=True)

  def conversations_list(self):
    # curl -s 'https://www.hackthebox.eu/api/conversations/list' -H 'Authorization: Bearer <apikey>' -H 'Content-Type: application/json;charset=utf-8' --data '' | jq .
    return self._post_http(endpoint="/conversations/list", data={}, authorize=True)

  def labs_switch(self, labname):
    # curl -s 'https://www.hackthebox.eu/api/labs/switch/usvip' -H 'Authorization: Bearer <apikey>' -H 'Content-Type: application/json;charset=utf-8' --data '' | jq .
    if labname.lower().strip() in ["eufree", "euvip", "euvipbeta", "usfree", "usvip"]:
      return self._post_http(endpoint="/labs/switch/%s" % (labname), data={}, authorize=True)

  def users_htb_connection_status(self):
    # curl -s 'https://www.hackthebox.eu/api/users/htb/connection/status' -H 'Authorization: Bearer <apikey>' -H 'Content-Type: application/json;charset=utf-8' --data '' | jq .
    return self._post_http(endpoint="/users/htb/connection/status", data={}, authorize=True)

  def users_htb_fortress_connection_status(self):
    # curl -s 'https://www.hackthebox.eu/api/users/htb/fortress/connection/status' -H 'Authorization: Bearer <apikey>' -H 'Content-Type: application/json;charset=utf-8' --data '' | jq .
    return self._post_http(endpoint="/users/htb/fortress/connection/status", data={}, authorize=True)

  def machines_assigned(self):
    # curl -s 'https://www.hackthebox.eu/api/machines/assigned' -H 'Authorization: Bearer <apikey>' | jq .
    return self._get_http(endpoint="/machines/assigned", authorize=True)

  def machines_owns(self):
    # curl -s 'https://www.hackthebox.eu/api/machines/owns' -H 'Authorization: Bearer <apikey>' | jq .
    return self._get_http(endpoint="/machines/owns", authorize=True)

  def machines_todo(self):
    # curl -s 'https://www.hackthebox.eu/api/machines/todo' -H 'Authorization: Bearer <apikey>' | jq .
    return self._get_http(endpoint="/machines/todo", authorize=True)

  def machines_spawned(self):
    # curl -s 'https://www.hackthebox.eu/api/machines/spawned' -H 'Authorization: Bearer <apikey>' | jq .
    return self._get_http(endpoint="/machines/spawned", authorize=True)

  def machines_todo_update(self, mid):
    # curl -s 'https://www.hackthebox.eu/api/machines/todo/update/1' -H 'Authorization: Bearer <apikey>' -H 'Content-Type: application/json;charset=utf-8' --data-raw '' | jq .
    return self._post_http(endpoint="/machines/todo/update/%d" % (mid), data={}, authorize=True)

  def machines_own(self, flag, difficulty, mid):
    # curl -s 'https://www.hackthebox.eu/api/machines/own' -H 'Authorization: Bearer <apikey>' -H 'Content-Type: application/json;charset=utf-8' --data-raw '{"flag":"<flag>","difficulty":40,"id":48}' | jq .
    return self._post_http(endpoint="/machines/own", data={"flag": flag, "difficulty": difficulty, "id": mid}, authorize=True)

  def vm_vip_assign(self, mid):
    # curl -s 'https://www.hackthebox.eu/api/vm/vip/assign/1' -H 'Authorization: Bearer <apikey>' -H 'Content-Type: application/json;charset=utf-8' --data-raw '' | jq .
    return self._post_http(endpoint="/vm/vip/assign/%d" % (mid), data={}, authorize=True)

  def vm_vip_extend(self, mid):
    # curl -s 'https://www.hackthebox.eu/api/vm/vip/extend/1' -H 'Authorization: Bearer <apikey>' -H 'Content-Type: application/json;charset=utf-8' --data-raw '' | jq .
    return self._post_http(endpoint="/vm/vip/extend/%d" % (mid), data={}, authorize=True)

  def vm_vip_remove(self, mid):
    # curl -s 'https://www.hackthebox.eu/api/vm/vip/remove/1' -H 'Authorization: Bearer <apikey>' -H 'Content-Type: application/json;charset=utf-8' --data-raw '' | jq .
    return self._post_http(endpoint="/vm/vip/remove/%d" % (mid), data={}, authorize=True)

  def vm_reset(self, mid):
    # curl -s 'https://www.hackthebox.eu/api/vm/reset/1' -H 'Authorization: Bearer <apikey>' -H 'Content-Type: application/json;charset=utf-8' --data-raw '' | jq .
    return self._post_http(endpoint="/vm/reset/%d" % (mid), data={}, authorize=True)
