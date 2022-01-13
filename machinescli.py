#!/usr/bin/env python3

import jq
import os
import re
import sys
import json
import argparse

import utils
from vulnhub import VulnHub
from hackthebox import HackTheBox
from tryhackme import TryHackMe


class MachinesCLI:
  def __init__(self):
    self.htbapi = HackTheBox(utils.expand_env(var="$HTBAPIKEY"))
    self.thmapi = TryHackMe()
    self.vhapi = VulnHub()
    self.jsonify = False
    self.gsheet = False
    self.showttps = False

    self.basedir = os.path.dirname(os.path.realpath(__file__))

    self.ownedfile = "%s/toolbox/bootstrap/owned" % (utils.expand_env(var="$HOME"))
    self.ownedlist = utils.load_file(self.ownedfile)

    self.oscplikefile = "%s/toolbox/bootstrap/oscplike" % (utils.expand_env(var="$HOME"))
    self.oscplikelist = utils.load_file(self.oscplikefile)

    self.statsfile = "%s/toolbox/bootstrap/machines.json" % (utils.expand_env(var="$HOME"))
    self.stats = utils.load_json(self.statsfile)
    if not self.stats:
      self.stats = {
        "counts": {},
        "machines": [],
      }

    self.queries = {
      "all": '.machines[]',
      "thm": '.machines[] | select(.infrastructure == "tryhackme")',
      "htb": '.machines[] | select(.infrastructure == "hackthebox")',
      "vh": '.machines[] | select(.infrastructure == "vulnhub")',
      "oscplike": '.machines[] | select(.oscplike == true)',
      "notoscplike": '.machines[] | select(.oscplike != true)',
      "owned": '.machines[] | select(.owned_user == true or .owned_root == true)',
      "ownedthm": '.machines[] | select(.infrastructure == "tryhackme" and (.owned_user == true or .owned_root == true))',
      "ownedhtb": '.machines[] | select(.infrastructure == "hackthebox" and (.owned_user == true or .owned_root == true))',
      "ownedvh": '.machines[] | select(.infrastructure == "vulnhub" and (.owned_user == true or .owned_root == true))',
      "oscplikethm": '.machines[] | select(.infrastructure == "tryhackme" and .oscplike == true)',
      "oscplikehtb": '.machines[] | select(.infrastructure == "hackthebox" and .oscplike == true)',
      "oscplikevh": '.machines[] | select(.infrastructure == "vulnhub" and .oscplike == true)',
      "ownedoscplike": '.machines[] | select(.oscplike == true and (.owned_user == true or .owned_root == true))',
      "notownedoscplike": '.machines[] | select(.oscplike == true and (.owned_user != true and .owned_root != true))',
      "ownednotoscplike": '.machines[] | select(.oscplike != true and (.owned_user == true or .owned_root == true))',
      "notownedthmoscplike": '.machines[] | select(.infrastructure == "tryhackme" and .oscplike == true and (.owned_user != true and .owned_root != true))',
      "ownednotthmoscplike": '.machines[] | select(.infrastructure == "tryhackme" and .oscplike != true and (.owned_user == true or .owned_root == true))',
      "notownedhtboscplike": '.machines[] | select(.infrastructure == "hackthebox" and .oscplike == true and (.owned_user != true and .owned_root != true))',
      "ownednothtboscplike": '.machines[] | select(.infrastructure == "hackthebox" and .oscplike != true and (.owned_user == true or .owned_root == true))',
      "notownedvhoscplike": '.machines[] | select(.infrastructure == "vulnhub" and .oscplike == true and (.owned_user != true and .owned_root != true))',
      "ownednotvhoscplike": '.machines[] | select(.infrastructure == "vulnhub" and .oscplike != true and (.owned_user == true or .owned_root == true))',
      "ownedthmoscplike": '.machines[] | select(.infrastructure == "tryhackme" and .oscplike == true and (.owned_user == true or .owned_root == true))',
      "ownedhtboscplike": '.machines[] | select(.infrastructure == "hackthebox" and .oscplike == true and (.owned_user == true or .owned_root == true))',
      "ownedvhoscplike": '.machines[] | select(.infrastructure == "vulnhub" and .oscplike == true and (.owned_user == true or .owned_root == true))',
    }
    self.queries["thmoscplike"] = self.queries["oscplikethm"]
    self.queries["thmoscplikeowned"] = self.queries["ownedthmoscplike"]
    self.queries["thmownedoscplike"] = self.queries["ownedthmoscplike"]

    self.queries["htboscplike"] = self.queries["oscplikehtb"]
    self.queries["htboscplikeowned"] = self.queries["ownedhtboscplike"]
    self.queries["htbownedoscplike"] = self.queries["ownedhtboscplike"]

    self.queries["vhoscplike"] = self.queries["oscplikevh"]
    self.queries["vhoscplikeowned"] = self.queries["ownedvhoscplike"]
    self.queries["vhownedoscplike"] = self.queries["ownedvhoscplike"]

    self.queries["oscplikeowned"] = self.queries["ownedoscplike"]
    self.queries["oscplikeownedthm"] = self.queries["ownedthmoscplike"]
    self.queries["oscplikethmowned"] = self.queries["ownedthmoscplike"]
    self.queries["oscplikeownedhtb"] = self.queries["ownedhtboscplike"]
    self.queries["oscplikehtbowned"] = self.queries["ownedhtboscplike"]
    self.queries["oscplikeownedvh"] = self.queries["ownedvhoscplike"]
    self.queries["oscplikevhowned"] = self.queries["ownedvhoscplike"]

    self.queries["ownedoscplikethm"] = self.queries["ownedthmoscplike"]
    self.queries["ownedoscplikehtb"] = self.queries["ownedhtboscplike"]
    self.queries["ownedoscplikevh"] = self.queries["ownedvhoscplike"]

    self.ipsc = {}

    self.vhcsvfile = "/tmp/oscplike.vh.csv"
    self.htbcsvfile = "/tmp/oscplike.htb.csv"

    self.points2difficulty = {
      0: "startingpoint",
      5: "info",
      10: "warmup",
      20: "easy",
      30: "medium",
      40: "hard",
      50: "insane",
    }

    self.corrections = {
      "devops": "devoops",
      "la casa de papel": "lacasadepapel",
    }

  def _do_count(self):
    self.stats["counts"]["htbnix"] = len(self._json_query('.machines[] | select(.infrastructure == "hackthebox" and .os and .os != "Windows") | .url'))
    self.stats["counts"]["htboscplike"] = len(self._json_query('.machines[] | select(.infrastructure == "hackthebox" and .oscplike) | .url'))
    self.stats["counts"]["htbwindows"] = len(self._json_query('.machines[] | select(.infrastructure == "hackthebox" and .os and .os == "Windows") | .url'))
    self.stats["counts"]["oscplikenix"] = len(self._json_query('.machines[] | select(.oscplike and .os and .os != "Windows") | .url'))
    self.stats["counts"]["oscplikewindows"] = len(self._json_query('.machines[] | select(.oscplike and .os and .os == "Windows") | .url'))
    self.stats["counts"]["ownedhtb"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .infrastructure == "hackthebox") | .url'))
    self.stats["counts"]["ownedhtbnix"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .infrastructure == "hackthebox" and .os and .os != "Windows") | .url'))
    self.stats["counts"]["ownedhtboscplike"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .infrastructure == "hackthebox" and .oscplike) | .url'))
    self.stats["counts"]["ownedhtbwindows"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .infrastructure == "hackthebox" and .os and .os == "Windows") | .url'))
    self.stats["counts"]["ownednix"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .os and .os != "Windows") | .url'))
    self.stats["counts"]["ownedoscplike"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .oscplike) | .url'))
    self.stats["counts"]["ownedoscplikenix"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .oscplike and .os and .os != "Windows") | .url'))
    self.stats["counts"]["ownedoscplikewindows"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .oscplike and .os and .os == "Windows") | .url'))
    self.stats["counts"]["ownedthm"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .infrastructure == "tryhackme") | .url'))
    self.stats["counts"]["ownedthmnix"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .infrastructure == "tryhackme" and .os and .os != "Windows") | .url'))
    self.stats["counts"]["ownedthmoscplike"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .infrastructure == "tryhackme" and .oscplike) | .url'))
    self.stats["counts"]["ownedthmwindows"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .infrastructure == "tryhackme" and .os and .os == "Windows") | .url'))
    self.stats["counts"]["ownedtotal"] = len(self._json_query('.machines[] | select(.owned_user or .owned_root) | .url'))
    self.stats["counts"]["ownedvh"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .infrastructure == "vulnhub") | .url'))
    self.stats["counts"]["ownedvhnix"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .infrastructure == "vulnhub" and .os and .os != "Windows") | .url'))
    self.stats["counts"]["ownedvhoscplike"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .infrastructure == "vulnhub" and .oscplike) | .url'))
    self.stats["counts"]["ownedvhwindows"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .infrastructure == "vulnhub" and .os and .os == "Windows") | .url'))
    self.stats["counts"]["ownedwindows"] = len(self._json_query('.machines[] | select((.owned_user or .owned_root) and .os and .os == "Windows") | .url'))
    self.stats["counts"]["thmnix"] = len(self._json_query('.machines[] | select(.infrastructure == "tryhackme" and .os and .os != "Windows") | .url'))
    self.stats["counts"]["thmoscplike"] = len(self._json_query('.machines[] | select(.infrastructure == "tryhackme" and .oscplike) | .oscplike'))
    self.stats["counts"]["thmwindows"] = len(self._json_query('.machines[] | select(.infrastructure == "tryhackme" and .os and .os == "Windows") | .url'))
    self.stats["counts"]["totalhtb"] = len(self._json_query('.machines[] | select(.infrastructure == "hackthebox") | .url'))
    self.stats["counts"]["totalnix"] = len(self._json_query('.machines[] | select(.os and .os != "Windows") | .url'))
    self.stats["counts"]["totaloscplike"] = len(self._json_query('.machines[] | select(.oscplike) | .url'))
    self.stats["counts"]["totalthm"] = len(self._json_query('.machines[] | select(.infrastructure == "tryhackme") | .url'))
    self.stats["counts"]["totaltotal"] = len(self._json_query('.machines[] | .url'))
    self.stats["counts"]["totalvh"] = len(self._json_query('.machines[] | select(.infrastructure == "vulnhub") | .url'))
    self.stats["counts"]["totalwindows"] = len(self._json_query('.machines[] | select(.os and .os == "Windows") | .url'))
    self.stats["counts"]["vhnix"] = len(self._json_query('.machines[] | select(.infrastructure == "vulnhub" and .os and .os != "Windows") | .url'))
    self.stats["counts"]["vhoscplike"] = len(self._json_query('.machines[] | select(.infrastructure == "vulnhub" and .oscplike) | .oscplike'))
    self.stats["counts"]["vhwindows"] = len(self._json_query('.machines[] | select(.infrastructure == "vulnhub" and .os and .os == "Windows") | .url'))
    self.stats["counts"]["perhtb"] = (self.stats["counts"]["ownedhtb"]/self.stats["counts"]["totalhtb"])*100 if self.stats["counts"]["totalhtb"] else 0
    self.stats["counts"]["perhtbnix"] = (self.stats["counts"]["ownedhtbnix"]/self.stats["counts"]["htbnix"])*100 if self.stats["counts"]["htbnix"] else 0
    self.stats["counts"]["perhtboscplike"] = (self.stats["counts"]["ownedhtboscplike"]/self.stats["counts"]["htboscplike"])*100 if self.stats["counts"]["htboscplike"] else 0
    self.stats["counts"]["perhtbwindows"] = (self.stats["counts"]["ownedhtbwindows"]/self.stats["counts"]["htbwindows"])*100 if self.stats["counts"]["htbwindows"] else 0
    self.stats["counts"]["pernix"] = (self.stats["counts"]["ownednix"]/self.stats["counts"]["totalnix"])*100 if self.stats["counts"]["totalnix"] else 0
    self.stats["counts"]["peroscplike"] = (self.stats["counts"]["ownedoscplike"]/self.stats["counts"]["totaloscplike"])*100 if self.stats["counts"]["totaloscplike"] else 0
    self.stats["counts"]["peroscplikenix"] = (self.stats["counts"]["ownedoscplikenix"]/self.stats["counts"]["oscplikenix"])*100 if self.stats["counts"]["oscplikenix"] else 0
    self.stats["counts"]["peroscplikewindows"] = (self.stats["counts"]["ownedoscplikewindows"]/self.stats["counts"]["oscplikewindows"])*100 if self.stats["counts"]["oscplikewindows"] else 0
    self.stats["counts"]["perthm"] = (self.stats["counts"]["ownedthm"]/self.stats["counts"]["totalthm"])*100 if self.stats["counts"]["totalthm"] else 0
    self.stats["counts"]["perthmnix"] = (self.stats["counts"]["ownedthmnix"]/self.stats["counts"]["thmnix"])*100 if self.stats["counts"]["thmnix"] else 0
    self.stats["counts"]["perthmoscplike"] = (self.stats["counts"]["ownedthmoscplike"]/self.stats["counts"]["thmoscplike"])*100 if self.stats["counts"]["thmoscplike"] else 0
    self.stats["counts"]["perthmwindows"] = (self.stats["counts"]["ownedthmwindows"]/self.stats["counts"]["thmwindows"])*100 if self.stats["counts"]["thmwindows"] else 0
    self.stats["counts"]["pertotal"] = (self.stats["counts"]["ownedtotal"]/self.stats["counts"]["totaltotal"])*100 if self.stats["counts"]["totaltotal"] else 0
    self.stats["counts"]["pervh"] = (self.stats["counts"]["ownedvh"]/self.stats["counts"]["totalvh"])*100 if self.stats["counts"]["totalvh"] else 0
    self.stats["counts"]["pervhnix"] = (self.stats["counts"]["ownedvhnix"]/self.stats["counts"]["vhnix"])*100 if self.stats["counts"]["vhnix"] else 0
    self.stats["counts"]["pervhoscplike"] = (self.stats["counts"]["ownedvhoscplike"]/self.stats["counts"]["vhoscplike"])*100 if self.stats["counts"]["vhoscplike"] else 0
    self.stats["counts"]["pervhwindows"] = (self.stats["counts"]["ownedvhwindows"]/self.stats["counts"]["vhwindows"])*100 if self.stats["counts"]["vhwindows"] else 0
    self.stats["counts"]["perwindows"] = (self.stats["counts"]["ownedwindows"]/self.stats["counts"]["totalwindows"])*100 if self.stats["counts"]["totalwindows"] else 0

  def _save_stats(self):
    self._do_count()
    utils.save_json(self.stats, self.statsfile)

  def _reload_stats(self):
    self.stats = utils.load_json(self.statsfile)

  def _save_owned(self):
    self.ownedlist = sorted(list(set(filter(None, self.ownedlist))))
    utils.save_file(self.ownedlist, self.ownedfile)

  def _reload_owned(self):
    self.ownedlist = utils.load_file(self.ownedfile)
    self.ownedlist = sorted(list(set(filter(None, self.ownedlist))))

  def _save_oscplike(self):
    self.oscplikelist = sorted(list(set(filter(None, self.oscplikelist))))
    utils.save_file(self.oscplikelist, self.oscplikefile)

  def _reload_oscplike(self):
    self.oscplikelist = utils.load_file(self.oscplikefile)
    self.oscplikelist = sorted(list(set(filter(None, self.oscplikelist))))

  def _filter_machines(self, valuelist, infrastructure="any", key=None):
    results, matched = [], []
    for value in valuelist:
      if value and value != "" and self.stats["machines"] and len(self.stats["machines"]):
        if not key:
          try:
            value = int(value)
            key = "id"
          except:
            pass
          if not key:
            if type(value) == str:
              if value.lower().strip().startswith("http"):
                key = "url"
              elif value.lower().strip().startswith("tryhackme#") or value.lower().strip().startswith("thm#"):
                key = "shortname"
                infrastructure = "thm"
                value = value.split("#", 1)[1]
              elif value.lower().strip().startswith("hackthebox#") or value.lower().strip().startswith("htb#"):
                key = "id"
                infrastructure = "htb"
                value = int(value.split("#", 1)[1])
              elif value.lower().strip().startswith("vulnhub#") or value.lower().strip().startswith("vh#"):
                key = "id"
                infrastructure = "vh"
                value = int(value.split("#", 1)[1])
              else:
                key = "name"
        else:
          key = key.lower().strip()
        for entry in self.stats["machines"]:
          infrastructure = infrastructure.lower().strip()
          if infrastructure in ["thm", "tryhackme"] and entry["infrastructure"] != "tryhackme":
            continue
          if infrastructure in ["htb", "hackthebox"] and entry["infrastructure"] != "hackthebox":
            continue
          if infrastructure in ["vh", "vulnhub"] and entry["infrastructure"] != "vulnhub":
            continue
          if key in ["name"]:
            if value.lower().strip() in entry[key].lower().strip() and entry["verbose_id"] not in matched:
              results.append(entry)
              matched.append(entry["verbose_id"])
          elif key in ["shortname"]:
            if value.lower().strip() in entry[key].lower().strip() and entry["shortname"] not in matched:
              results.append(entry)
              matched.append(entry["verbose_id"])
          elif key in ["url"]:
            if value.lower().strip() == entry[key].lower().strip() and entry["verbose_id"] not in matched:
              results.append(entry)
              matched.append(entry["verbose_id"])
          elif key in ["id"]:
            if value == entry[key] and entry["verbose_id"] not in matched:
              results.append(entry)
              matched.append(entry["verbose_id"])
          elif key in ["description"]:
            if entry.get("description"):
              if value.lower().strip() in entry[key].lower().strip() and entry["verbose_id"] not in matched:
                results.append(entry)
                matched.append(entry["verbose_id"])
            if entry.get("writeups") and entry["writeups"].get("ippsec"):
              for desc in entry["writeups"]["ippsec"]["description"]:
                if value.lower().strip() in desc.lower() and entry["verbose_id"] not in matched:
                  results.append(entry)
                  matched.append(entry["verbose_id"])
                  results[-1]["writeups"]["ippsec"]["description"] = { desc:entry["writeups"]["ippsec"]["description"][desc] }
        key = None

    return results

  def _json_query(self, query):
    try:
      return jq.compile(query).input(self.stats).all()
    except:
      return []

  def _update_ippsec(self):
    self.ipsc = {
      "url": "https://ippsec.rocks/dataset.json",
      "count": 0,
      "entries": {}
    }
    entries = utils.download_json(self.ipsc["url"])
    for entry in entries:
      if not entry.get("videoId", None):
        continue
      name = utils.strip_html(entry["machine"])
      video_url = "https://www.youtube.com/watch?v=%s&t=0" % (entry["videoId"])
      hours = int(entry["timestamp"]["minutes"] // 60); minutes = entry["timestamp"]["minutes"] - (hours*60)
      timestamp = "%02d:%02d:%02d" % (hours, minutes, entry["timestamp"]["seconds"])
      totalseconds = (entry["timestamp"]["minutes"]*60) + entry["timestamp"]["seconds"]
      tsurl = "https://www.youtube.com/watch?v=%s&t=%ds" % (entry["videoId"], totalseconds)
      desc = "%s - %s" % (timestamp, utils.strip_html(entry["line"]))
      if name not in self.ipsc["entries"]:
        self.ipsc["count"] += 1
        self.ipsc["entries"][name] = {
          "video_url": video_url,
          "description": {
            desc: tsurl
          }
        }
      else:
        self.ipsc["entries"][name]["description"][desc] = tsurl
    if len(self.ipsc["entries"]):
      for machine in self.stats["machines"]:
        if self.ipsc and self.ipsc.get("entries") and self.ipsc["entries"]:
          for entry in self.ipsc["entries"]:
            if machine["infrastructure"] in entry.lower().strip() and machine["name"].lower().strip() in entry.lower().strip():
              machine["writeups"] = {
                "ippsec": {
                  "name": entry,
                  "video_url": self.ipsc["entries"][entry]["video_url"],
                  "description": self.ipsc["entries"][entry]["description"],
                }
              }
      utils.info("[update.ippsec] added %d machine writeup descriptions from ippsec" % (self.ipsc["count"]))

  def _update_oscplike(self, fullupdate=False):
    self._reload_oscplike()
    if fullupdate:
      utils.download("https://docs.google.com/spreadsheets/d/1dwSMIAPIam0PuRBkCiDI88pU3yzrqqHkDtBngUHNCw8/export?format=csv&gid=1839402159", self.htbcsvfile)
      with open(self.htbcsvfile) as fp: htbdata = fp.read()
      lines = htbdata.split("\n")
      htboscplike = []
      for line in lines[5:]:
        for token in line.split(",", 3):
          if token and token != "":
            token = token.lower().replace(" [linux]", "").replace(" [windows]", "").strip()
            token = self.corrections[token] if token in self.corrections else token
            # token is a name, find url from self.stats
            query = '.machines[] | select(.infrastructure == "hackthebox" and .shortname == "%s") | .url' % (token)
            result = self._json_query(query)
            if result and len(result):
              htboscplike.append(result[0])
      self.oscplikelist += htboscplike
      utils.download("https://docs.google.com/spreadsheets/d/1dwSMIAPIam0PuRBkCiDI88pU3yzrqqHkDtBngUHNCw8/export?format=csv&gid=0", self.vhcsvfile)
      with open(self.vhcsvfile) as fp: vhdata = fp.read()
      lines = vhdata.split("\n")
      vhoscplike = []
      for line in lines[5:]:
        celldata = line.replace('",', '"___')
        for entry in celldata.split("___"):
          if not entry: continue
          match = re.search(r'vulnhub\.com/entry/(.+),(\d+)', entry)
          if match:
            name, mid, url = match.groups()[0], int(match.groups()[1]), "https://www.vulnhub.com/entry/%s,%s/" % (match.groups()[0], match.groups()[1])
            vhoscplike.append(token)
      self.oscplikelist += vhoscplike
      self._save_oscplike()
    for machine in self.stats["machines"]:
      if machine["url"] in self.oscplikelist:
        machine["oscplike"] = True
      else:
        machine["oscplike"] = False
    self._save_stats()
    utils.info("[update.oscplike] added %d oscplike machines from various sources" % (len(self.oscplikelist)))

  def _update_owned(self):
    self.ownedlist.extend([x["url"] for x in self._filter_machines([x["id"] for x in self.htbapi.machines_owns()], infrastructure="htb")])
    self._save_owned()
    for machine in self.stats["machines"]:
      if machine["url"] in self.ownedlist:
        machine["owned_user"] = True
        machine["owned_root"] = True
      else:
        machine["owned_user"] = False
        machine["owned_root"] = False
    self._save_stats()
    utils.info("[update.owned] updated owned stats for %d machines" % (len(self.ownedlist)))

  def _update_hackthebox(self):
    difficulty = self.htbapi.machines_difficulty()
    machines = self.htbapi.machines_startingpoint_all()
    machines += self.htbapi.machines_get_all()
    htbmachines = {}
    for machine in machines:
      url = "https://app.hackthebox.eu/machines/%d" % (machine["id"])
      htbmachines[url] = machine
    trackedhtb = self._json_query('.machines[] | select(.infrastructure == "hackthebox") | .url')
    totalhtb = htbmachines.keys()
    deltahtb = list(set(totalhtb) - set(trackedhtb))
    utils.info("[update.hackthebox] tracked: %d, total: %d, delta: %d" % (len(trackedhtb), len(totalhtb), len(deltahtb)))
    if len(deltahtb):
      total = len(deltahtb)
      for idx, deltaurl in enumerate(deltahtb):
        print("[update.hackthebox][%d/%d] adding stats for %s" % (idx+1, total, deltaurl))
        matchdict = htbmachines[deltaurl]
        if "avatar_thumb" in matchdict:
          matchdict["matrix"] = self.htbapi.machines_get_matrix(matchdict["id"]); del matchdict["matrix"]["success"]
          del matchdict["avatar_thumb"]
        else:
          matchdict["points"] = 0
          matchdict["matrix"] = {
            "aggregate": [],
            "maker": []
          }
        matchdict["infrastructure"] = "hackthebox"
        matchdict["verbose_id"] = "hackthebox#%d" % (matchdict["id"])
        matchdict["difficulty"] = self.points2difficulty[matchdict["points"]]
        matchdict["shortname"] = matchdict["name"].lower().strip()
        matchdict["url"] = "https://app.hackthebox.eu/machines/%d" % (matchdict["id"])
        matchdict["difficulty_ratings"] = None
        for entry in difficulty:
          if entry["id"] == matchdict["id"]:
            matchdict["difficulty_ratings"] = entry["difficulty_ratings"] if entry["difficulty_ratings"] else []
        self.stats["machines"].append(matchdict)
      utils.info("[update.hackthebox] added %d new machines (total: %d)" % (len(deltahtb), len(self._json_query('.machines[] | select(.infrastructure == "hackthebox") | .url'))))

  def _update_vulnhub(self):
    urls = self.vhapi._get_all_machine_urls()
    vhmachines = {}
    for url in urls:
      vhmachines[url] = None
    trackedvh = self._json_query('.machines[] | select(.infrastructure == "vulnhub") | .url')
    totalvh = vhmachines.keys()
    deltavh = list(set(totalvh) - set(trackedvh))
    utils.info("[update.vulnhub] tracked: %d, total: %d, delta: %d" % (len(trackedvh), len(totalvh), len(deltavh)))
    if len(deltavh):
      total = len(deltavh)
      for idx, deltaurl in enumerate(deltavh):
        print("[update.vulnhub][%d/%d] adding stats for %s" % (idx+1, total, deltaurl))
        vhmachines[deltaurl] = self.vhapi._parse_machine_page(deltaurl)
        matchdict = vhmachines[deltaurl]
        if not matchdict["name"]:
          continue
        del matchdict["avatar_thumb"]
        matchdict["infrastructure"] = "vulnhub"
        matchdict["verbose_id"] = "vulnhub#%d" % (matchdict["id"])
        matchdict["difficulty"] = self.points2difficulty[matchdict["points"]] if matchdict["points"] else None
        matchdict["shortname"] = matchdict["name"].lower().strip()
        matchdict["owned_user"], matchdict["owned_root"] = False, False
        matchdict["difficulty_ratings"] = None
        self.stats["machines"].append(matchdict)
      utils.info("[update.vulnhub] added %d new machines (total: %d)" % (len(deltavh), len(self._json_query('.machines[] | select(.infrastructure == "vulnhub") | .url'))))

  def _update_tryhackme(self):
    rooms = self.thmapi.rooms()["rooms"]
    thmrooms = {}
    for room in rooms:
      url = "https://tryhackme.com/room/%s" % (room["code"])
      thmrooms[url] = room
    trackedthm = self._json_query('.machines[] | select(.infrastructure == "tryhackme") | .url')
    totalthm = thmrooms.keys()
    deltathm = list(set(totalthm) - set(trackedthm))
    utils.info("[update.tryhackme] tracked: %d, total: %d, delta: %d" % (len(trackedthm), len(totalthm), len(deltathm)))
    if len(deltathm):
      d2p = dict((v,k) for k,v in self.points2difficulty.items())
      total = len(deltathm)
      for idx, deltaurl in enumerate(deltathm):
        print("[update.tryhackme][%d/%d] adding stats for %s" % (idx+1, total, deltaurl))
        matchdict = {
          "description": thmrooms[deltaurl]["description"],
          "difficulty": thmrooms[deltaurl]["difficulty"],
          "difficulty_ratings": None,
          "id": "tryhackme#%s" % (thmrooms[deltaurl]["code"]),
          "infrastructure": "tryhackme",
          "maker": {
            "id": None,
            "name": thmrooms[deltaurl]["creator"],
            "url": None,
          },
          "name": thmrooms[deltaurl]["title"],
          "os": None,
          "oscplike": None,
          "owned_root": False,
          "owned_user": False,
          "points": d2p[thmrooms[deltaurl]["difficulty"]],
          "release": thmrooms[deltaurl]["published"] if "published" in thmrooms[deltaurl] else thmrooms[deltaurl]["created"],
          "series": {
            "id": None,
            "name": None,
            "url": None,
          },
          "shortname": thmrooms[deltaurl]["code"],
          "url": deltaurl,
          "verbose_id": "tryhackme#%s" % (thmrooms[deltaurl]["code"]),
        }
        matchdict["difficulty_ratings"] = None
        self.stats["machines"].append(matchdict)
      utils.info("[update.tryhackme] added %d new machines (total: %d)" % (len(deltathm), len(self._json_query('.machines[] | select(.infrastructure == "tryhackme") | .url'))))

  def update(self, fullupdate=False):
    if fullupdate:
      self.stats["machines"] = []

    # fetch new machine stats from resp. platforms
    self._update_tryhackme()
    self._update_hackthebox()
    self._update_vulnhub()

    # for all machines, update owned/ippsec/oscplike stats
    self._update_owned()
    self._update_ippsec()
    self._update_oscplike(fullupdate=fullupdate)

    # show latest counts
    self.counts()

  def counts(self):
    if self.jsonify:
      utils.to_json(self.stats["counts"])
    else:
      header, rows = ["#", "Total", "TryHackMe", "HackTheBox", "VulnHub", "OSCPlike"], []
      rows.append("___".join([x for x in [
        "%s" % (utils.green("Total")),
        "%s/%s (%s)" % (utils.green(self.stats["counts"]["ownedtotal"]), utils.green(self.stats["counts"]["totaltotal"]), utils.green("%.2f%%" % (self.stats["counts"]["pertotal"]))),
        "%s/%s (%s)" % (utils.green(self.stats["counts"]["ownedthm"]), utils.green(self.stats["counts"]["totalthm"]), utils.green("%.2f%%" % (self.stats["counts"]["perthm"]))),
        "%s/%s (%s)" % (utils.green(self.stats["counts"]["ownedhtb"]), utils.green(self.stats["counts"]["totalhtb"]), utils.green("%.2f%%" % (self.stats["counts"]["perhtb"]))),
        "%s/%s (%s)" % (utils.green(self.stats["counts"]["ownedvh"]), utils.green(self.stats["counts"]["totalvh"]), utils.green("%.2f%%" % (self.stats["counts"]["pervh"]))),
        "%s/%s (%s)" % (utils.red(self.stats["counts"]["ownedoscplike"]), utils.red(self.stats["counts"]["totaloscplike"]), utils.red("%.2f%%" % (self.stats["counts"]["peroscplike"]))),
      ]]))
      rows.append("___".join([str(x) for x in [
        utils.yellow("Windows"),
        "%s/%s (%s)" % (utils.yellow(self.stats["counts"]["ownedwindows"]), utils.yellow(self.stats["counts"]["totalwindows"]), utils.yellow("%.2f%%" % (self.stats["counts"]["perwindows"]))),
        "%s/%s (%s)" % (utils.yellow(self.stats["counts"]["ownedthmwindows"]), utils.yellow(self.stats["counts"]["thmwindows"]), utils.yellow("%.2f%%" % (self.stats["counts"]["perthmwindows"]))),
        "%s/%s (%s)" % (utils.yellow(self.stats["counts"]["ownedhtbwindows"]), utils.yellow(self.stats["counts"]["htbwindows"]), utils.yellow("%.2f%%" % (self.stats["counts"]["perhtbwindows"]))),
        "%s/%s (%s)" % (utils.yellow(self.stats["counts"]["ownedvhwindows"]), utils.yellow(self.stats["counts"]["vhwindows"]), utils.yellow("%.2f%%" % (self.stats["counts"]["pervhwindows"]))),
        "%s/%s (%s)" % (utils.yellow(self.stats["counts"]["ownedoscplikewindows"]), utils.yellow(self.stats["counts"]["oscplikewindows"]), utils.yellow("%.2f%%" % (self.stats["counts"]["peroscplikewindows"]))),
      ]]))
      rows.append("___".join([str(x) for x in [
        utils.magenta("*nix"),
        "%s/%s (%s)" % (utils.magenta(self.stats["counts"]["ownednix"]), utils.magenta(self.stats["counts"]["totalnix"]), utils.magenta("%.2f%%" % (self.stats["counts"]["pernix"]))),
        "%s/%s (%s)" % (utils.magenta(self.stats["counts"]["ownedthmnix"]), utils.magenta(self.stats["counts"]["thmnix"]), utils.magenta("%.2f%%" % (self.stats["counts"]["perthmnix"]))),
        "%s/%s (%s)" % (utils.magenta(self.stats["counts"]["ownedhtbnix"]), utils.magenta(self.stats["counts"]["htbnix"]), utils.magenta("%.2f%%" % (self.stats["counts"]["perhtbnix"]))),
        "%s/%s (%s)" % (utils.magenta(self.stats["counts"]["ownedvhnix"]), utils.magenta(self.stats["counts"]["vhnix"]), utils.magenta("%.2f%%" % (self.stats["counts"]["pervhnix"]))),
        "%s/%s (%s)" % (utils.magenta(self.stats["counts"]["ownedoscplikenix"]), utils.magenta(self.stats["counts"]["oscplikenix"]), utils.magenta("%.2f%%" % (self.stats["counts"]["peroscplikenix"]))),
      ]]))
      rows.append("___".join([str(x) for x in [
        utils.red("OSCPlike"),
        "%s/%s (%s)" % (utils.red(self.stats["counts"]["ownedoscplike"]), utils.red(self.stats["counts"]["totaloscplike"]), utils.red("%.2f%%" % (self.stats["counts"]["peroscplike"]))),
        "%s/%s (%s)" % (utils.red(self.stats["counts"]["ownedthmoscplike"]), utils.red(self.stats["counts"]["thmoscplike"]), utils.red("%.2f%%" % (self.stats["counts"]["perthmoscplike"]))),
        "%s/%s (%s)" % (utils.red(self.stats["counts"]["ownedhtboscplike"]), utils.red(self.stats["counts"]["htboscplike"]), utils.red("%.2f%%" % (self.stats["counts"]["perhtboscplike"]))),
        "%s/%s (%s)" % (utils.red(self.stats["counts"]["ownedvhoscplike"]), utils.red(self.stats["counts"]["vhoscplike"]), utils.red("%.2f%%" % (self.stats["counts"]["pervhoscplike"]))),
        utils.red(""),
      ]]))
      aligndict = {
        "#": "r",
        "Total": "l",
        "TryHackMe": "l",
        "HackTheBox": "l",
        "VulnHub": "l",
        "OSCPlike": "l",
      }
      utils.to_table(header, rows, delim="___", aligndict=aligndict)

  def query(self, querystr):
    if querystr.strip().lower() in self.queries:
      query = self.queries[querystr.lower().strip()] if querystr.lower().strip() in self.queries else None
    else:
      query = querystr.strip()
    if query:
      utils.show_machines(self._json_query(query), jsonify=self.jsonify, gsheet=self.gsheet, showttps=self.showttps)

  def search(self, searchkey):
    machines = self._filter_machines([searchkey], infrastructure="any", key="description")
    results = []
    for machine in machines:
      if machine.get("description"):
        machine["search_url"] = machine["verbose_id"]
      else:
        for desc, url in machine["writeups"]["ippsec"]["description"].items():
          machine["search_text"] = desc
          machine["search_url"] = utils.yturl2verboseid(url)
          break
      results.append(machine)
    utils.show_machines(machines, jsonify=self.jsonify, gsheet=self.gsheet, showttps=self.showttps)

  def info(self, searchkey):
    searchkeys = [searchkey] if searchkey.startswith("http") else [x.strip() for x in searchkey.split(",")]
    utils.show_machines(self._filter_machines(searchkeys, infrastructure="any"), jsonify=self.jsonify, gsheet=self.gsheet, showttps=self.showttps)

  def own(self, args):
    searchkey, flag = args.split(",", 1)
    matches = self._filter_machines([searchkey], infrastructure="any")
    if len(matches) > 1:
      utils.error("found multiple (%d) machines for searchkey \"%s\"" % (len(matches), searchkey))
    else:
      for entry in matches:
        if entry["infrastructure"] in ["htb", "hackthebox"]:
          # submit flag to htb and show response
          resp = self.htbapi.machines_own(flag, entry["points"], entry["id"])
          utils.to_json(resp)
        else:
          # update machines.json: trust user for thm and vh
          self.ownedlist.append(entry["url"])
    # refresh owned stats, recount and update machines.json
    self._update_owned()

  def htb_stats(self):
    stats = {
      "connection_status": self.htbapi.users_htb_connection_status(),
      "global_stats": self.htbapi.stats_global(),
      "overview_stats": self.htbapi.stats_overview(),
    }
    utils.to_json(stats)

  def htb_todos(self):
    utils.show_machines(self._filter_machines([x["id"] for x in self.htbapi.machines_todo()], infrastructure="htb"), jsonify=self.jsonify, gsheet=self.gsheet, showttps=self.showttps)

  def htb_assigned(self):
    utils.show_machines(self._filter_machines([x["id"] for x in self.htbapi.machines_assigned()], infrastructure="htb"), jsonify=self.jsonify, gsheet=self.gsheet, showttps=self.showttps)

  def htb_owned(self):
    utils.show_machines(self._filter_machines([x["id"] for x in self.htbapi.machines_owns()], infrastructure="htb"), jsonify=self.jsonify, gsheet=self.gsheet, showttps=self.showttps)

  def htb_spawned(self):
    utils.show_machines(self._filter_machines([x["id"] for x in self.htbapi.machines_spawned()], infrastructure="htb"), jsonify=self.jsonify, gsheet=self.gsheet, showttps=self.showttps)

  def htb_terminating(self):
    utils.show_machines(self._filter_machines([x["id"] for x in self.htbapi.machines_terminating()], infrastructure="htb"), jsonify=self.jsonify, gsheet=self.gsheet, showttps=self.showttps)

  def htb_resetting(self):
    utils.show_machines(self._filter_machines([x["id"] for x in self.htbapi.machines_resetting()], infrastructure="htb"), jsonify=self.jsonify, gsheet=self.gsheet, showttps=self.showttps)

  def htb_expiry(self):
    expirydict = self.htbapi.machines_expiry()
    machines = self._filter_machines([x["id"] for x in expirydict], infrastructure="htb")
    results = []
    for machine in machines:
      for entry in expirydict:
        if entry["id"] == machine["id"]:
          machine["expires_at"] = entry["expires_at"]
          results.append(machine)
    utils.show_machines(results, jsonify=self.jsonify, gsheet=self.gsheet, showttps=self.showttps)

  def htb_assign(self, searchkey):
    matches = self._filter_machines([searchkey], infrastructure="htb")
    if len(matches) > 1:
      utils.error("found multiple (%d) machines for searchkey \"%s\"" % (len(matches), searchkey))
    else:
      for entry in matches:
        utils.to_json(self.htbapi.vm_vip_assign(entry["id"]))

  def htb_extend(self, searchkey):
    matches = self._filter_machines([searchkey], infrastructure="htb")
    if len(matches) > 1:
      utils.error("found multiple (%d) machines for searchkey \"%s\"" % (len(matches), searchkey))
    else:
      for entry in matches:
        utils.to_json(self.htbapi.vm_vip_extend(entry["id"]))

  def htb_reset(self, searchkey):
    matches = self._filter_machines([searchkey], infrastructure="htb")
    if len(matches) > 1:
      utils.error("found multiple (%d) machines for searchkey \"%s\"" % (len(matches), searchkey))
    else:
      for entry in matches:
        utils.to_json(self.htbapi.vm_reset(entry["id"]))

  def htb_remove(self, searchkey):
    matches = self._filter_machines([searchkey], infrastructure="htb")
    if len(matches) > 1:
      utils.error("found multiple (%d) machines for searchkey \"%s\"" % (len(matches), searchkey))
    else:
      for entry in matches:
        utils.to_json(self.htbapi.vm_vip_remove(entry["id"]))

  def htb_todo(self, searchkey):
    for entry in [x["id"] for x in self._filter_machines([searchkey], infrastructure="htb")]:
      self.htbapi.machines_todo_update(entry)
    self.htb_todos()

  def thm_stats(self):
    utils.to_json(self.thmapi.stats_global())


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="%s (v%s): Command-line interface for %s, %s and %s machines." % (utils.blue_bold("machinescli"), utils.green_bold("0.1"), utils.magenta_bold("HackTheBox"), utils.cyan_bold("TryHackMe"), utils.yellow_bold("VulnHub")))

  # global flag to switch output mode; useful for debugging with jq
  ggroup = parser.add_mutually_exclusive_group()
  ggroup.add_argument('-j', '--jsonify', required=False, action='store_true', default=False, help='show raw json output (disable default tabular output)')
  ggroup.add_argument('-g', '--gsheet', required=False, action='store_true', default=False, help='show ghseet csv output (disable default tabular output)')
  ggroup.add_argument('-t', '--showttps', required=False, action='store_true', default=False, help='show ttps if machine writeup is available')

  mcgroup = parser.add_mutually_exclusive_group()

  # update htb|vh|oscplike stats
  # will perform live api querying for htb, web crawls for vh and oscplike lists
  mcgroup.add_argument('--update', required=False, action='store_true', default=False, help='update local stats file %s' % (utils.black_bold("(takes time)")))

  # localized querying and listing of results from stats file (covers all supported platforms and lists (htb|vh and oscplike as of v0.1)
  # results could differ from htbgroup calls if local stats file has not been updated in a while
  lsgroup = mcgroup.add_mutually_exclusive_group()
  lsgroup.add_argument('--counts', required=False, action='store_true', default=False, help='show counts for all machines')
  lsgroup.add_argument('--query', required=False, action='store', help='show stats for queried machines (all|thm|htb|vh|oscplike|notoscplike|owned|ownedthm|ownedhtb|ownedvh|oscplikethm|oscplikehtb|oscplikevh|ownedoscplike|notownedoscplike|ownednotoscplike|ownedthmoscplike|ownedhtboscplike|ownedvhoscplike)')

  lsgroup.add_argument('--info', required=False, action='store', help='query local stats file for machine name|url|id')
  lsgroup.add_argument('--search', required=False, action='store', help='query local stats file for machine writeup|description')
  lsgroup.add_argument('--own', required=False, action='store', help='toggle owned status for a machine name|url|id,flag')

  htbgroup = mcgroup.add_mutually_exclusive_group()
  htbgroup.add_argument('--htb-assign', required=False, action='store', help='assign a hackthebox machine name|url|id')
  htbgroup.add_argument('--htb-assigned', required=False, action='store_true', default=False, help='show hackthebox assigned machines')
  htbgroup.add_argument('--htb-owned', required=False, action='store_true', default=False, help='show hackthebox owned machines')
  htbgroup.add_argument('--htb-expiry', required=False, action='store_true', default=False, help='show expiry details for hackthebox machines')
  htbgroup.add_argument('--htb-extend', required=False, action='store', help='extend a hackthebox machine name|url|id')
  htbgroup.add_argument('--htb-remove', required=False, action='store', help='remove a hackthebox machine name|url|id')
  htbgroup.add_argument('--htb-reset', required=False, action='store', help='reset a hackthebox machine name|url|id')
  htbgroup.add_argument('--htb-resetting', required=False, action='store_true', default=False, help='show hackthebox machines currently listed for reset')
  htbgroup.add_argument('--htb-spawned', required=False, action='store_true', default=False, help='show hackthebox spawned machines')
  htbgroup.add_argument('--htb-stats', required=False, action='store_true', default=False, help='show hackthebox platform stats')
  htbgroup.add_argument('--htb-terminating', required=False, action='store_true', default=False, help='show hackthebox machines currently listed for termination')
  htbgroup.add_argument('--htb-todo', required=False, action='store', help='add to todo list a hackthebox machine name|url|id')
  htbgroup.add_argument('--htb-todos', required=False, action='store_true', default=False, help='show hackthebox todo machines')

  thmgroup = mcgroup.add_mutually_exclusive_group()
  thmgroup.add_argument('--thm-stats', required=False, action='store_true', default=False, help='show tryhackme platform stats')

  args = parser.parse_args()

  mcli = MachinesCLI()

  if args.jsonify:
    mcli.jsonify = True

  if args.gsheet:
    mcli.gsheet = True

  if args.showttps:
    mcli.showttps = True

  if args.update:
    mcli.update()

  elif args.counts:
    mcli.counts()

  elif args.query:
    mcli.query(args.query)

  elif args.search:
    mcli.search(args.search)

  elif args.info:
    mcli.info(args.info)

  elif args.own:
    mcli.own(args.own)

  elif args.htb_stats:
    mcli.htb_stats()

  elif args.htb_todos:
    mcli.htb_todos()

  elif args.htb_assigned:
    mcli.htb_assigned()

  elif args.htb_owned:
    mcli.htb_owned()

  elif args.htb_spawned:
    mcli.htb_spawned()

  elif args.htb_terminating:
    mcli.htb_terminating()

  elif args.htb_resetting:
    mcli.htb_resetting()

  elif args.htb_expiry:
    mcli.htb_expiry()

  elif args.htb_assign:
    mcli.htb_assign(args.htb_assign)

  elif args.htb_extend:
    mcli.htb_extend(args.htb_extend)

  elif args.htb_reset:
    mcli.htb_reset(args.htb_reset)

  elif args.htb_remove:
    mcli.htb_remove(args.htb_remove)

  elif args.htb_todo:
    mcli.htb_todo(args.htb_todo)

  elif args.thm_stats:
    mcli.thm_stats()

  else:
    parser.print_help()
