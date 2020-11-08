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
    self.htbapi = HackTheBox(utils.expand_env(var="$HTB_API_KEY"))
    self.thmapi = TryHackMe()
    self.vhapi = VulnHub()
    self.jsonify = False
    self.gsheet = False

    self.basedir = os.path.dirname(os.path.realpath(__file__))

    self.ownedfile = "%s/toolbox/bootstrap/owned" % (utils.expand_env(var="$HOME"))
    self.ownedlist = utils.load_file(self.ownedfile)

    self.statsfile = "%s/toolbox/bootstrap/machines.json" % (utils.expand_env(var="$HOME"))
    self.stats = utils.load_json(self.statsfile)

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
    self.olsearchkeys = {
      "htb": None,
      "vh": None,
    }

    self.points2difficulty = {
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

  def _save_stats(self):
    utils.save_json(self.stats, self.statsfile)
    utils.debug("saved stats for %d machines to '%s'" % (self.stats["counts"]["totaltotal"], self.statsfile))

  def _reload_stats(self):
    self.stats = utils.load_json(self.statsfile)
    utils.debug("reloaded stats for %d machines from '%s'" % (len(self.stats["counts"]["totaltotal"]), self.statsfile))

  def _save_owned(self):
    self.ownedlist = sorted(list(set(filter(None, self.ownedlist))))
    utils.save_file(self.ownedlist, self.ownedfile)
    utils.debug("saved owned list with %d entries to '%s'" % (len(self.ownedlist), self.ownedfile))

  def _reload_owned(self):
    self.ownedlist = utils.load_file(self.ownedfile)
    self.ownedlist = sorted(list(set(filter(None, self.ownedlist))))
    utils.debug("reloaded owned list with %d entries from '%s'" % (len(self.ownedlist), self.ownedfile))

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
            if entry.get("writeups"):
              for desc in entry["writeups"]["ippsec"]["description"]:
                if value.lower().strip() in desc.lower() and entry["verbose_id"] not in matched:
                  results.append(entry)
                  matched.append(entry["verbose_id"])
                  results[-1]["writeups"]["ippsec"]["description"] = { desc:entry["writeups"]["ippsec"]["description"][desc] }
        key = None

    return results

  def json_query(self, query):
    try:
      return jq.compile(query).input(self.stats).all()
    except:
      return []

  def _update_ippsec(self):
    utils.info("updating ippsec writeup descriptions...")
    self.ipsc = {
      "url": "https://ippsec.rocks/dataset.json",
      "count": 0,
      "entries": {}
    }
    entries = utils.download_json(self.ipsc["url"])
    for entry in entries:
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
      utils.info("got descriptions for %d writeup videos" % (self.ipsc["count"]))

  def _update_oscplike(self):
    utils.info("updating oscplike tryhackme machines list...")
    self.olsearchkeys["thm"] = []
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/alfred"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/attacktivedirectory"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/blaster"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/blue"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/blueprint"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/brainpan"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/brainstorm"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/bufferoverflowprep"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/corp"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/dailybugle"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/gamezone"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/gatekeeper"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/hackpark"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/introexploitdevelopment"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/kenobi"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/linuxprivesc"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/lordoftheroot"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/mrrobot"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/powershell"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/retro"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/skynet"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/steelmountain"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/tomghost"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/tonythetiger"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/vulnversity"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/windows10privesc"]
    self.olsearchkeys["thm"] += ["https://tryhackme.com/room/windowsprivescarena"]
    utils.debug("found %d entries for oscplike tryhackme machines" % (len(self.olsearchkeys["thm"])))

    # get listing of oscplike htb machines
    self.olsearchkeys["htb"] = []
    self.olsearchkeys["htb"] += ["remote", "sauna", "servmon", "traceback"] # https://medium.com/@peregerinebunny/my-oscp-journey-d3addc26f07b
    self.olsearchkeys["htb"] += ["heist"] # https://medium.com/@bondo.mike/htb-heist-390c079a20e5
    utils.info("updating oscplike hackthebox machines list...")
    self.olsearchkeys["htb"] = list(set(self.olsearchkeys["htb"]))
    utils.download("https://docs.google.com/spreadsheets/d/1dwSMIAPIam0PuRBkCiDI88pU3yzrqqHkDtBngUHNCw8/export?format=csv&gid=1839402159", self.htbcsvfile)
    utils.debug("saved tjnull's oscplike hackthebox machines list to '%s'" % (self.htbcsvfile))
    with open(self.htbcsvfile) as fp:
      htbdata = fp.read()
    lines = htbdata.split("\n")
    if lines[2] == 'Linux Boxes:,Windows Boxes:,"More challenging than OSCP, but good practice:",':
      for line in lines[3:]:
        for token in line.split(",", 3):
          if token and token != "":
            token = token.lower().replace(" [linux]", "").replace(" [windows]", "").strip()
            token = self.corrections[token] if token in self.corrections else token
            self.olsearchkeys["htb"].append(token)
    utils.debug("found %d entries for oscplike hackthebox machines" % (len(self.olsearchkeys["htb"])))

    # get listing of oscplike vulnhub machines
    self.olsearchkeys["vh"] = []
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/photographer-1,519/"]
    # https://www.abatchy.com/2017/02/oscp-like-vulnhub-vms
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/devrandom-scream,47/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/brainpan-1,51/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/fristileaks-13,133/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/hacklab-vulnix,48/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/imf-1,162/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/kioptrix-2014-5,62/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/kioptrix-level-1-1,22/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/kioptrix-level-11-2,23/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/kioptrix-level-12-3,24/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/kioptrix-level-13-4,25/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/mr-robot-1,151/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/pwnlab-init,158/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/pwnos-20-pre-release,34/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/sickos-12,144/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/skytower-1,96/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/stapler-1,150/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/vulnos-2,147/"]
    # https://zayotic.com/posts/oscp-like-vulnhub-vms/
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/basic-pentesting-1,216/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/basic-pentesting-2,241/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/born2root-1,197/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/born2root-2,291/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/brainpan-1,51/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/brainpan-2,56/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/brainpan-3,121/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/breach-1,152/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/breach-21,159/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/breach-301,177/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/covfefe-1,199/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/darknet-10,120/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/dc-1-1,292/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/dc-2,311/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/dc-3,312/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/dc-4,313/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/dc-5,314/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/dc-6,315/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/derpnstink-1,221/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/devrandom-scream,47/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/devrandom-sleepy,123/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/digitalworldlocal-bravery,281/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/digitalworldlocal-development,280/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/digitalworldlocal-mercy-v2,263/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/dina-101,200/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/droopy-v02,143/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/fowsniff-1,262/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/fristileaks-13,133/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/hackinos-1,295/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/hacklab-vulnix,48/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/haste-1,203/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/imf-1,162/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/kioptrix-2014-5,62/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/kioptrix-level-1-1,22/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/kioptrix-level-11-2,23/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/kioptrix-level-12-3,24/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/kioptrix-level-13-4,25/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/lazysysadmin-1,205/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/linsecurity-1,244/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/lord-of-the-root-101,129/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/mr-robot-1,151/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/nineveh-v03,222/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/node-1,252/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/pwnlab-init,158/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/pwnlab-init,158/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/pwnos-20-pre-release,34/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/raven-1,256/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/raven-2,269/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/rickdiculouslyeasy-1,207/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/sickos-11,132/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/sickos-12,144/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/sickos-12,144/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/skytower-1,96/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/smashthetux-101,138/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/solidstate-1,261/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/stapler-1,150/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/symfonos-1,322/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/toppo-1,245/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/vulnos-2,147/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/wakanda-1,251/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/wintermute-1,239/"]
    self.olsearchkeys["vh"] += ["https://www.vulnhub.com/entry/xtreme-vulnerable-web-application-xvwa-1,209/"]

    utils.info("updating oscplike vulnhub machines list...")
    self.olsearchkeys["vh"] = list(set(self.olsearchkeys["vh"]))
    utils.download("https://docs.google.com/spreadsheets/d/1dwSMIAPIam0PuRBkCiDI88pU3yzrqqHkDtBngUHNCw8/export?format=csv&gid=0", self.vhcsvfile)
    utils.debug("saved tjnull's oscplike vulnhub machines list to '%s'" % (self.vhcsvfile))
    with open(self.vhcsvfile) as fp:
      vhdata = fp.read()
    lines = vhdata.split("\n")
    if lines[3].split(",")[0] == "VMs Highlighted in pink are considered to be similar to OSCP":
      for line in lines[4:]:
        celldata = line.replace('",', '"___')
        match = re.search(r'vulnhub\.com/entry/(.+),(\d+)', celldata.split("___", 1)[0])
        if match:
          name, mid, url = match.groups()[0], int(match.groups()[1]), "https://www.vulnhub.com/entry/%s,%s/" % (match.groups()[0], match.groups()[1])
          self.olsearchkeys["vh"].append(url)
    utils.debug("found %d entries for oscplike vulnhub machines" % (len(self.olsearchkeys["vh"])))

  def _refresh_htb_owned(self):
    # get owned list from htb api
    owned = self._filter_machines([x["id"] for x in self.htbapi.machines_owns()], infrastructure="htb")
    # add all owned htb machines to in-memory owned list
    self.ownedlist.extend([x["url"] for x in owned])
    # dedup ownedlist
    self.ownedlist = sorted(list(set(self.ownedlist)))
    # save the updated owned list locally and refreh in-memory list
    self._save_owned()
    return owned

  def _update_hackthebox(self, stats):
    utils.info("updating hackthebox machines...")
    # use this opportunity to refresh htb results for owned machines
    owned = self._refresh_htb_owned()
    difficulty = self.htbapi.machines_difficulty()
    for machine in self.htbapi.machines_get_all():
      matchdict = machine
      del matchdict["avatar_thumb"]
      matchdict["infrastructure"] = "hackthebox"
      matchdict["verbose_id"] = "hackthebox#%d" % (matchdict["id"])
      matchdict["difficulty"] = self.points2difficulty[machine["points"]]
      matchdict["shortname"] = machine["name"].lower().strip()
      matchdict["matrix"] = self.htbapi.machines_get_matrix(matchdict["id"]); del matchdict["matrix"]["success"]
      matchdict["oscplike"] = True if matchdict["shortname"] in self.olsearchkeys["htb"] else False
      matchdict["url"] = "https://www.hackthebox.eu/home/machines/profile/%d" % (machine["id"])
      matchdict["owned_user"], matchdict["owned_root"] = False, False
      for entry in self.ownedlist:
        if entry.lower().strip() == matchdict["url"].lower().strip():
          matchdict["owned_user"], matchdict["owned_root"] = True, True
          break
      matchdict["difficulty_ratings"] = None
      for entry in difficulty:
        if entry["id"] == matchdict["id"]:
          matchdict["difficulty_ratings"] = entry["difficulty_ratings"] if entry["difficulty_ratings"] else []
      for entry in self.ipsc["entries"]:
        if matchdict["infrastructure"] in entry.lower().strip() and matchdict["name"].lower().strip() in entry.lower().strip():
          matchdict["writeups"] = {
            "ippsec": {
              "name": entry,
              "video_url": self.ipsc["entries"][entry]["video_url"],
              "description": self.ipsc["entries"][entry]["description"],
            }
          }

      stats["counts"]["totaltotal"] += 1
      stats["counts"]["totalhtb"] += 1

      if matchdict["oscplike"]:
        stats["counts"]["totaloscplike"] += 1
        stats["counts"]["htboscplike"] += 1

      if matchdict["os"]:
        if matchdict["os"].lower() == "windows":
          stats["counts"]["totalwindows"] += 1
          stats["counts"]["htbwindows"] += 1
          if matchdict["oscplike"]:
            stats["counts"]["oscplikewindows"] += 1
        else:
          stats["counts"]["totalnix"] += 1
          stats["counts"]["htbnix"] += 1
          if matchdict["oscplike"]:
            stats["counts"]["oscplikenix"] += 1

      if matchdict["owned_user"] or matchdict["owned_root"]:
        stats["counts"]["ownedhtb"] += 1
        stats["counts"]["ownedtotal"] += 1
        if matchdict["os"] and matchdict["os"].lower() != "windows":
          stats["counts"]["ownedhtbnix"] += 1
          stats["counts"]["ownednix"] += 1
        if matchdict["os"] and matchdict["os"].lower() == "windows":
          stats["counts"]["ownedhtbwindows"] += 1
          stats["counts"]["ownedwindows"] += 1
        if matchdict["oscplike"]:
          stats["counts"]["ownedhtboscplike"] += 1
          stats["counts"]["ownedoscplike"] += 1
        if matchdict["oscplike"] and matchdict["os"] and matchdict["os"].lower() != "windows":
          stats["counts"]["ownedoscplikenix"] += 1
        if matchdict["oscplike"] and matchdict["os"] and matchdict["os"].lower() == "windows":
          stats["counts"]["ownedoscplikewindows"] += 1
  
      stats["machines"].append(matchdict)
    utils.info("found %d hackthebox machines" % (stats["counts"]["totalhtb"]))
    return stats

  def _update_vulnhub(self, stats):
    utils.info("updating vulnhub machines...")
    self._reload_owned()
    for machine in self.vhapi.get_all_machine_stats():
      if not machine["name"]:
        continue
      matchdict = machine
      del matchdict["avatar_thumb"]
      matchdict["infrastructure"] = "vulnhub"
      matchdict["verbose_id"] = "vulnhub#%d" % (matchdict["id"])
      matchdict["difficulty"] = self.points2difficulty[machine["points"]] if machine["points"] else None
      matchdict["shortname"] = machine["name"].lower().strip()
      matchdict["oscplike"] = True if matchdict["url"] in self.olsearchkeys["vh"] else False
      matchdict["owned_user"], matchdict["owned_root"] = False, False
      for entry in self.ownedlist:
        if entry.lower().strip() == matchdict["url"].lower().strip():
          matchdict["owned_user"], matchdict["owned_root"] = True, True
          break
      matchdict["difficulty_ratings"] = None
      for entry in self.ipsc["entries"]:
        if matchdict["infrastructure"] in entry.lower().strip() and matchdict["name"].lower().strip() in entry.lower().strip():
          matchdict["writeups"] = {
            "ippsec": {
              "name": entry,
              "video_url": self.ipsc["entries"][entry]["video_url"],
              "description": self.ipsc["entries"][entry]["description"],
            }
          }

      stats["counts"]["totaltotal"] += 1
      stats["counts"]["totalvh"] += 1

      if matchdict["oscplike"]:
        stats["counts"]["totaloscplike"] += 1
        stats["counts"]["vhoscplike"] += 1

      if matchdict["os"]:
        if matchdict["os"].lower() == "windows":
          stats["counts"]["totalwindows"] += 1
          stats["counts"]["vhwindows"] += 1
          if matchdict["oscplike"]:
            stats["counts"]["oscplikewindows"] += 1
        else:
          stats["counts"]["totalnix"] += 1
          stats["counts"]["vhnix"] += 1
          if matchdict["oscplike"]:
            stats["counts"]["oscplikenix"] += 1

      if matchdict["owned_user"] or matchdict["owned_root"]:
        stats["counts"]["ownedvh"] += 1
        stats["counts"]["ownedtotal"] += 1
        if matchdict["os"] and matchdict["os"].lower() != "windows":
          stats["counts"]["ownedvhnix"] += 1
          stats["counts"]["ownednix"] += 1
        if matchdict["os"] and matchdict["os"].lower() == "windows":
          stats["counts"]["ownedvhwindows"] += 1
          stats["counts"]["ownedwindows"] += 1
        if matchdict["oscplike"]:
          stats["counts"]["ownedvhoscplike"] += 1
          stats["counts"]["ownedoscplike"] += 1
        if matchdict["oscplike"] and matchdict["os"] and matchdict["os"].lower() != "windows":
          stats["counts"]["ownedoscplikenix"] += 1
        if matchdict["oscplike"] and matchdict["os"] and matchdict["os"].lower() == "windows":
          stats["counts"]["ownedoscplikewindows"] += 1

      stats["machines"].append(machine)
    utils.info("found %d vulnhub machines" % (stats["counts"]["totalvh"]))
    return stats

  def _update_tryhackme(self, stats):
    utils.info("updating tryhackme machines...")
    d2p = dict((v,k) for k,v in self.points2difficulty.items())
    for room in self.thmapi.rooms():
      matchdict = {
        "description": room["description"],
        "difficulty": room["difficulty"],
        "difficulty_ratings": None,
        "id": "tryhackme#%s" % (room["code"]),
        "infrastructure": "tryhackme",
        "maker": {
          "id": None,
          "name": room["creator"],
          "url": None,
        },
        "name": room["title"],
        "os": None,
        "oscplike": None,
        "owned_root": False,
        "owned_user": False,
        "points": d2p[room["difficulty"]],
        "release": room["published"],
        "series": {
          "id": None,
          "name": None,
          "url": None,
        },
        "shortname": room["code"],
        "url": "https://tryhackme.com/room/%s" % (room["code"]),
        "verbose_id": "tryhackme#%s" % (room["code"]),
      }

      matchdict["oscplike"] = True if matchdict["url"] in self.olsearchkeys["thm"] else False
      matchdict["owned_user"], matchdict["owned_root"] = False, False
      for entry in self.ownedlist:
        if entry.lower().strip() == matchdict["url"].lower().strip():
          matchdict["owned_user"], matchdict["owned_root"] = True, True
          break
      matchdict["difficulty_ratings"] = None
      for entry in self.ipsc["entries"]:
        if matchdict["infrastructure"] in entry.lower().strip() and matchdict["name"].lower().strip() in entry.lower().strip():
          matchdict["writeups"] = {
            "ippsec": {
              "name": entry,
              "video_url": self.ipsc["entries"][entry]["video_url"],
              "description": self.ipsc["entries"][entry]["description"],
            }
          }

      stats["counts"]["totaltotal"] += 1
      stats["counts"]["totalthm"] += 1

      if matchdict["oscplike"]:
        stats["counts"]["totaloscplike"] += 1
        stats["counts"]["thmoscplike"] += 1

      if matchdict["os"]:
        if matchdict["os"].lower() == "windows":
          stats["counts"]["totalwindows"] += 1
          stats["counts"]["thmwindows"] += 1
          if matchdict["oscplike"]:
            stats["counts"]["oscplikewindows"] += 1
        else:
          stats["counts"]["totalnix"] += 1
          stats["counts"]["thmnix"] += 1
          if matchdict["oscplike"]:
            stats["counts"]["oscplikenix"] += 1

      if matchdict["owned_user"] or matchdict["owned_root"]:
        stats["counts"]["ownedthm"] += 1
        stats["counts"]["ownedtotal"] += 1
        if matchdict["os"] and matchdict["os"].lower() != "windows":
          stats["counts"]["ownedthmnix"] += 1
          stats["counts"]["ownednix"] += 1
        if matchdict["os"] and matchdict["os"].lower() == "windows":
          stats["counts"]["ownedthmwindows"] += 1
          stats["counts"]["ownedwindows"] += 1
        if matchdict["oscplike"]:
          stats["counts"]["ownedthmoscplike"] += 1
          stats["counts"]["ownedoscplike"] += 1
        if matchdict["oscplike"] and matchdict["os"] and matchdict["os"].lower() != "windows":
          stats["counts"]["ownedoscplikenix"] += 1
        if matchdict["oscplike"] and matchdict["os"] and matchdict["os"].lower() == "windows":
          stats["counts"]["ownedoscplikewindows"] += 1

      stats["machines"].append(matchdict)
    utils.info("found %d tryhackme machines" % (stats["counts"]["totalthm"]))
    return stats

  def update(self):
    stats = {
      "counts": {
        "htbnix": 0,
        "htboscplike": 0,
        "htbwindows": 0,
        "oscplikenix": 0,
        "oscplikewindows": 0,
        "ownedhtb": 0,
        "ownedhtbnix": 0,
        "ownedhtboscplike": 0,
        "ownedhtbwindows": 0,
        "ownednix": 0,
        "ownedoscplike": 0,
        "ownedoscplikenix": 0,
        "ownedoscplikewindows": 0,
        "ownedthm": 0,
        "ownedthmnix": 0,
        "ownedthmoscplike": 0,
        "ownedthmwindows": 0,
        "ownedtotal": 0,
        "ownedvh": 0,
        "ownedvhnix": 0,
        "ownedvhoscplike": 0,
        "ownedvhwindows": 0,
        "ownedwindows": 0,
        "perhtb": 0,
        "perhtbnix": 0,
        "perhtboscplike": 0,
        "perhtbwindows": 0,
        "pernix": 0,
        "peroscplike": 0,
        "peroscplikenix": 0,
        "peroscplikewindows": 0,
        "perthm": 0,
        "perthmnix": 0,
        "perthmoscplike": 0,
        "perthmwindows": 0,
        "pertotal": 0,
        "pervh": 0,
        "pervhnix": 0,
        "pervhoscplike": 0,
        "pervhwindows": 0,
        "perwindows": 0,
        "thmnix": 0,
        "thmoscplike": 0,
        "thmwindows": 0,
        "totalhtb": 0,
        "totalnix": 0,
        "totaloscplike": 0,
        "totalthm": 0,
        "totaltotal": 0,
        "totalvh": 0,
        "totalwindows": 0,
        "vhnix": 0,
        "vhoscplike": 0,
        "vhwindows": 0,
      },
      "machines": [],
    }

    # useful metadata sources
    self._update_ippsec()
    self._update_oscplike()

    # infrastructure/platform sources
    stats = self._update_tryhackme(stats)
    stats = self._update_hackthebox(stats)
    stats = self._update_vulnhub(stats)

    stats["counts"]["perthm"] = (stats["counts"]["ownedthm"]/stats["counts"]["totalthm"])*100 if stats["counts"]["totalthm"] else 0
    stats["counts"]["perthmnix"] = (stats["counts"]["ownedthmnix"]/stats["counts"]["thmnix"])*100 if stats["counts"]["thmnix"] else 0
    stats["counts"]["perthmwindows"] = (stats["counts"]["ownedthmwindows"]/stats["counts"]["thmwindows"])*100 if stats["counts"]["thmwindows"] else 0
    stats["counts"]["perthmoscplike"] = (stats["counts"]["ownedthmoscplike"]/stats["counts"]["thmoscplike"])*100 if stats["counts"]["thmoscplike"] else 0

    stats["counts"]["perhtb"] = (stats["counts"]["ownedhtb"]/stats["counts"]["totalhtb"])*100 if stats["counts"]["totalhtb"] else 0
    stats["counts"]["perhtbnix"] = (stats["counts"]["ownedhtbnix"]/stats["counts"]["htbnix"])*100 if stats["counts"]["htbnix"] else 0
    stats["counts"]["perhtbwindows"] = (stats["counts"]["ownedhtbwindows"]/stats["counts"]["htbwindows"])*100 if stats["counts"]["htbwindows"] else 0
    stats["counts"]["perhtboscplike"] = (stats["counts"]["ownedhtboscplike"]/stats["counts"]["htboscplike"])*100 if stats["counts"]["htboscplike"] else 0

    utils.to_json(stats["counts"])

    stats["counts"]["pervh"] = (stats["counts"]["ownedvh"]/stats["counts"]["totalvh"])*100 if stats["counts"]["totalvh"] else 0
    stats["counts"]["pervhnix"] = (stats["counts"]["ownedvhnix"]/stats["counts"]["vhnix"])*100 if stats["counts"]["vhnix"] else 0
    stats["counts"]["pervhwindows"] = (stats["counts"]["ownedvhwindows"]/stats["counts"]["vhwindows"])*100 if stats["counts"]["vhwindows"] else 0
    stats["counts"]["pervhoscplike"] = (stats["counts"]["ownedvhoscplike"]/stats["counts"]["vhoscplike"])*100 if stats["counts"]["vhoscplike"] else 0

    stats["counts"]["peroscplike"] = (stats["counts"]["ownedoscplike"]/stats["counts"]["totaloscplike"])*100 if stats["counts"]["totaloscplike"] else 0
    stats["counts"]["peroscplikenix"] = (stats["counts"]["ownedoscplikenix"]/stats["counts"]["oscplikenix"])*100 if stats["counts"]["oscplikenix"] else 0
    stats["counts"]["peroscplikewindows"] = (stats["counts"]["ownedoscplikewindows"]/stats["counts"]["oscplikewindows"])*100 if stats["counts"]["oscplikewindows"] else 0

    stats["counts"]["pernix"] = (stats["counts"]["ownednix"]/stats["counts"]["totalnix"])*100 if stats["counts"]["totalnix"] else 0
    stats["counts"]["perwindows"] = (stats["counts"]["ownedwindows"]/stats["counts"]["totalwindows"])*100 if stats["counts"]["totalwindows"] else 0
    stats["counts"]["pertotal"] = (stats["counts"]["ownedtotal"]/stats["counts"]["totaltotal"])*100 if stats["counts"]["totaltotal"] else 0

    self.stats = stats
    self._save_stats()
    utils.show_machines(self.stats["machines"], jsonify=self.jsonify, gsheet=self.gsheet)

  def counts(self):
    if self.jsonify:
      utils.to_json(self.stats["counts"])
    else:
      header, rows = ["#", "Total", "HackTheBox", "VulnHub", "OSCPlike"], []
      rows.append("___".join([x for x in [
        "%s" % (utils.green("Total")),
        "%s/%s (%s)" % (utils.green(self.stats["counts"]["ownedtotal"]), utils.green(self.stats["counts"]["totaltotal"]), utils.green("%.2f%%" % (self.stats["counts"]["pertotal"]))),
        "%s/%s (%s)" % (utils.green(self.stats["counts"]["ownedhtb"]), utils.green(self.stats["counts"]["totalhtb"]), utils.green("%.2f%%" % (self.stats["counts"]["perhtb"]))),
        "%s/%s (%s)" % (utils.green(self.stats["counts"]["ownedvh"]), utils.green(self.stats["counts"]["totalvh"]), utils.green("%.2f%%" % (self.stats["counts"]["pervh"]))),
        "%s/%s (%s)" % (utils.red(self.stats["counts"]["ownedoscplike"]), utils.red(self.stats["counts"]["totaloscplike"]), utils.red("%.2f%%" % (self.stats["counts"]["peroscplike"]))),
      ]]))
      rows.append("___".join([str(x) for x in [
        utils.yellow("Windows"),
        "%s/%s (%s)" % (utils.yellow(self.stats["counts"]["ownedwindows"]), utils.yellow(self.stats["counts"]["totalwindows"]), utils.yellow("%.2f%%" % (self.stats["counts"]["perwindows"]))),
        "%s/%s (%s)" % (utils.yellow(self.stats["counts"]["ownedhtbwindows"]), utils.yellow(self.stats["counts"]["htbwindows"]), utils.yellow("%.2f%%" % (self.stats["counts"]["perhtbwindows"]))),
        "%s/%s (%s)" % (utils.yellow(self.stats["counts"]["ownedvhwindows"]), utils.yellow(self.stats["counts"]["vhwindows"]), utils.yellow("%.2f%%" % (self.stats["counts"]["pervhwindows"]))),
        "%s/%s (%s)" % (utils.yellow(self.stats["counts"]["ownedoscplikewindows"]), utils.yellow(self.stats["counts"]["oscplikewindows"]), utils.yellow("%.2f%%" % (self.stats["counts"]["peroscplikewindows"]))),
      ]]))
      rows.append("___".join([str(x) for x in [
        utils.magenta("*nix"),
        "%s/%s (%s)" % (utils.magenta(self.stats["counts"]["ownednix"]), utils.magenta(self.stats["counts"]["totalnix"]), utils.magenta("%.2f%%" % (self.stats["counts"]["pernix"]))),
        "%s/%s (%s)" % (utils.magenta(self.stats["counts"]["ownedhtbnix"]), utils.magenta(self.stats["counts"]["htbnix"]), utils.magenta("%.2f%%" % (self.stats["counts"]["perhtbnix"]))),
        "%s/%s (%s)" % (utils.magenta(self.stats["counts"]["ownedvhnix"]), utils.magenta(self.stats["counts"]["vhnix"]), utils.magenta("%.2f%%" % (self.stats["counts"]["pervhnix"]))),
        "%s/%s (%s)" % (utils.magenta(self.stats["counts"]["ownedoscplikenix"]), utils.magenta(self.stats["counts"]["oscplikenix"]), utils.magenta("%.2f%%" % (self.stats["counts"]["peroscplikenix"]))),
      ]]))
      rows.append("___".join([str(x) for x in [
        utils.red("OSCPlike"),
        "%s/%s (%s)" % (utils.red(self.stats["counts"]["ownedoscplike"]), utils.red(self.stats["counts"]["totaloscplike"]), utils.red("%.2f%%" % (self.stats["counts"]["peroscplike"]))),
        "%s/%s (%s)" % (utils.red(self.stats["counts"]["ownedhtboscplike"]), utils.red(self.stats["counts"]["htboscplike"]), utils.red("%.2f%%" % (self.stats["counts"]["perhtboscplike"]))),
        "%s/%s (%s)" % (utils.red(self.stats["counts"]["ownedvhoscplike"]), utils.red(self.stats["counts"]["vhoscplike"]), utils.red("%.2f%%" % (self.stats["counts"]["pervhoscplike"]))),
        utils.red(""),
      ]]))
      aligndict = {
        "#": "c",
        "Total": "r",
        "HackTheBox": "r",
        "VulnHub": "r",
        "OSCPlike": "r",
      }
      utils.to_table(header, rows, delim="___", aligndict=aligndict)

  def query(self, querystr):
    if querystr.strip().lower() in self.queries:
      query = self.queries[querystr.lower().strip()] if querystr.lower().strip() in self.queries else None
    else:
      query = querystr.strip()
    if query:
      utils.show_machines(self.json_query(query), jsonify=self.jsonify, gsheet=self.gsheet)

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
    utils.show_machines(machines, jsonify=self.jsonify, gsheet=self.gsheet)

  def info(self, searchkey):
    searchkeys = [searchkey] if searchkey.startswith("http") else [x.strip() for x in searchkey.split(",")]
    utils.show_machines(self._filter_machines(searchkeys, infrastructure="any"), jsonify=self.jsonify, gsheet=self.gsheet)

  def own(self, args):
    searchkey, flag = args.split(",", 1)
    matches = self._filter_machines([searchkey], infrastructure="any")
    if len(matches) > 1:
      utils.error("found multiple (%d) machines for searchkey \"%s\"" % (len(matches), searchkey))
    else:
      for entry in matches:
        self.ownedlist.append(entry["url"])
        self._save_owned()
        if entry["infrastructure"] in ["htb", "hackthebox"]:
          resp = self.htbapi.machines_own(flag, entry["points"], entry["id"])
          utils.to_json(resp)
      # based on api reponse, update machines.json

  def htb_stats(self):
    stats = {
      "connection_status": self.htbapi.users_htb_connection_status(),
      "global_stats": self.htbapi.stats_global(),
      "overview_stats": self.htbapi.stats_overview(),
    }
    utils.to_json(stats)

  def htb_todos(self):
    utils.show_machines(self._filter_machines([x["id"] for x in self.htbapi.machines_todo()], infrastructure="htb"), jsonify=self.jsonify, gsheet=self.gsheet)

  def htb_assigned(self):
    utils.show_machines(self._filter_machines([x["id"] for x in self.htbapi.machines_assigned()], infrastructure="htb"), jsonify=self.jsonify, gsheet=self.gsheet)

  def htb_owned(self):
    utils.show_machines(self._filter_machines([x["id"] for x in self.htbapi.machines_owns()], infrastructure="htb"), jsonify=self.jsonify, gsheet=self.gsheet)

  def htb_spawned(self):
    utils.show_machines(self._filter_machines([x["id"] for x in self.htbapi.machines_spawned()], infrastructure="htb"), jsonify=self.jsonify, gsheet=self.gsheet)

  def htb_terminating(self):
    utils.show_machines(self._filter_machines([x["id"] for x in self.htbapi.machines_terminating()], infrastructure="htb"), jsonify=self.jsonify, gsheet=self.gsheet)

  def htb_resetting(self):
    utils.show_machines(self._filter_machines([x["id"] for x in self.htbapi.machines_resetting()], infrastructure="htb"), jsonify=self.jsonify, gsheet=self.gsheet)

  def htb_expiry(self):
    expirydict = self.htbapi.machines_expiry()
    machines = self._filter_machines([x["id"] for x in expirydict], infrastructure="htb")
    results = []
    for machine in machines:
      for entry in expirydict:
        if entry["id"] == machine["id"]:
          machine["expires_at"] = entry["expires_at"]
          results.append(machine)
    utils.show_machines(results, jsonify=self.jsonify, gsheet=self.gsheet)

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


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="%s (v%s): Command-line interface for %s, %s and %s machines." % (utils.blue_bold("machinescli"), utils.green_bold("0.1"), utils.magenta_bold("HackTheBox"), utils.cyan_bold("TryHackMe"), utils.yellow_bold("VulnHub")))

  # global flag to switch output mode; useful for debugging with jq
  ggroup = parser.add_mutually_exclusive_group()
  ggroup.add_argument('-j', '--jsonify', required=False, action='store_true', default=False, help='show raw json output (disable default tabular output)')
  ggroup.add_argument('-g', '--gsheet', required=False, action='store_true', default=False, help='show ghseet csv output (disable default tabular output)')

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

  args = parser.parse_args()

  mcli = MachinesCLI()

  if args.jsonify:
    mcli.jsonify = True

  if args.gsheet:
    mcli.gsheet = True

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

  else:
    parser.print_help()
