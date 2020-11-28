#!/usr/bin/env python3

import re
import utils
from bs4 import BeautifulSoup


class VulnHub:
  def __init__(self):
    self.version = "0.1"
    self.baseurl = "https://www.vulnhub.com/"
    self.useragent = "Python VH Client/%s" % (self.version)
    self.headers = { "User-Agent": self.useragent }

    self.difficulty = {
      "easy": [ ## 20pts
        "https://www.vulnhub.com/entry/21ltr-scene-1,3/",
        "https://www.vulnhub.com/entry/basic-pentesting-1,216/",
        "https://www.vulnhub.com/entry/basic-pentesting-2,241/",
        "https://www.vulnhub.com/entry/billu-b0x,188/",
        "https://www.vulnhub.com/entry/billu-b0x-2,238/",
        "https://www.vulnhub.com/entry/born2root-1,197/",
        "https://www.vulnhub.com/entry/bossplayersctf-1,375/",
        "https://www.vulnhub.com/entry/broken-gallery,344/",
        "https://www.vulnhub.com/entry/bsides-vancouver-2018-workshop,231/",
        "https://www.vulnhub.com/entry/btrsys-v1,195/",
        "https://www.vulnhub.com/entry/btrsys-v21,196/",
        "https://www.vulnhub.com/entry/bulldog-1,211/",
        "https://www.vulnhub.com/entry/connect-the-dots-1,384/",
        "https://www.vulnhub.com/entry/dc-1,292/",
        "https://www.vulnhub.com/entry/dc-2,311/",
        "https://www.vulnhub.com/entry/dc-32,312/",
        "https://www.vulnhub.com/entry/de-ice-s1120,10/",
        "https://www.vulnhub.com/entry/derpnstink-1,221/",
        "https://www.vulnhub.com/entry/dina-101,200/",
        "https://www.vulnhub.com/entry/dpwwn-1,342/",
        "https://www.vulnhub.com/entry/evm-1,391/",
        "https://www.vulnhub.com/entry/fourandsix-201,266/",
        "https://www.vulnhub.com/entry/fowsniff-1,262/",
        "https://www.vulnhub.com/entry/g0rmint-1,214/",
        "https://www.vulnhub.com/entry/geisha-1,481/",
        "https://www.vulnhub.com/entry/grimtheripper-1,350/",
        "https://www.vulnhub.com/entry/hackademic-rtb1,17/",
        "https://www.vulnhub.com/entry/hackfest2016-orcus,182/",
        "https://www.vulnhub.com/entry/hackfest2016-quaoar,180/",
        "https://www.vulnhub.com/entry/hackfest2016-sedna,181/",
        "https://www.vulnhub.com/entry/hacklab-vulnix,48/",
        "https://www.vulnhub.com/entry/hackme-1,330/",
        "https://www.vulnhub.com/entry/haste-1,203/",
        "https://www.vulnhub.com/entry/holynix-v1,20/",
        "https://www.vulnhub.com/entry/jarbas-1,232/",
        "https://www.vulnhub.com/entry/katana-1,482/",
        "https://www.vulnhub.com/entry/kevgir-1,137/",
        "https://www.vulnhub.com/entry/kioptrix-2014-5,62/",
        "https://www.vulnhub.com/entry/kioptrix-level-1-1,22/",
        "https://www.vulnhub.com/entry/kioptrix-level-11-2,23/",
        "https://www.vulnhub.com/entry/kioptrix-level-12-3,24/",
        "https://www.vulnhub.com/entry/kioptrix-level-13-4,25/",
        "https://www.vulnhub.com/entry/lampiao-1,249/",
        "https://www.vulnhub.com/entry/lampsecurity-ctf4,83/",
        "https://www.vulnhub.com/entry/lampsecurity-ctf5,84/",
        "https://www.vulnhub.com/entry/lampsecurity-ctf7,86/",
        "https://www.vulnhub.com/entry/lazysysadmin-1,205/",
        "https://www.vulnhub.com/entry/mhz_cxf-c1f,471/",
        "https://www.vulnhub.com/entry/milnet-1,148/",
        "https://www.vulnhub.com/entry/misdirection-1,371/",
        "https://www.vulnhub.com/entry/mission-pumpkin-v10-pumpkinfestival,329/",
        "https://www.vulnhub.com/entry/mission-pumpkin-v10-pumpkingarden,321/",
        "https://www.vulnhub.com/entry/moria-11,187/",
        "https://www.vulnhub.com/entry/my-file-server-1,432/",
        "https://www.vulnhub.com/entry/nullbyte-1,126/",
        "https://www.vulnhub.com/entry/pentester-lab-from-sql-injection-to-shell,80/",
        "https://www.vulnhub.com/entry/pentester-lab-s2-052,206/",
        "https://www.vulnhub.com/entry/pluck-1,178/",
        "https://www.vulnhub.com/entry/pwnlab-init,158/",
        "https://www.vulnhub.com/entry/pwnos-10,33/",
        "https://www.vulnhub.com/entry/pwnos-20-pre-release,34/",
        "https://www.vulnhub.com/entry/rickdiculouslyeasy-1,207/",
        "https://www.vulnhub.com/entry/sahu-11,421/",
        "https://www.vulnhub.com/entry/sar-1,425/",
        "https://www.vulnhub.com/entry/seattle-v03,145/",
        "https://www.vulnhub.com/entry/secos-1,88/",
        "https://www.vulnhub.com/entry/sectalks-bne0x00-minotaur,139/",
        "https://www.vulnhub.com/entry/sectalks-bne0x03-simple,141/",
        "https://www.vulnhub.com/entry/sickos-11,132/",
        "https://www.vulnhub.com/entry/sickos-12,144/",
        "https://www.vulnhub.com/entry/sp-eric,274/",
        "https://www.vulnhub.com/entry/sputnik-1,301/",
        "https://www.vulnhub.com/entry/stapler-1,150/",
        "https://www.vulnhub.com/entry/sunset-1,339/",
        "https://www.vulnhub.com/entry/sunset-dawn,341/",
        "https://www.vulnhub.com/entry/symfonos-1,322/",
        "https://www.vulnhub.com/entry/symfonos-52,415/",
        "https://www.vulnhub.com/entry/ted-1,327/",
        "https://www.vulnhub.com/entry/the-library-1,334/",
        "https://www.vulnhub.com/entry/the-library-2,335/",
        "https://www.vulnhub.com/entry/tophatsec-freshly,118/",
        "https://www.vulnhub.com/entry/tophatsec-zorz,117/",
        "https://www.vulnhub.com/entry/toppo-1,245/",
        "https://www.vulnhub.com/entry/tr0ll-1,100/",
        "https://www.vulnhub.com/entry/typhoon-102,267/",
        "https://www.vulnhub.com/entry/unknowndevice64-2,297/",
        "https://www.vulnhub.com/entry/vulnos-1,60/",
        "https://www.vulnhub.com/entry/vulnos-2,147/",
        "https://www.vulnhub.com/entry/wallabys-nightmare-v102,176/",
        "https://www.vulnhub.com/entry/westwild-11,338/",
      ],
      "medium": [ ## 30pts
        "https://www.vulnhub.com/entry/2much-1,319/",
        "https://www.vulnhub.com/entry/64base-101,173/",
        "https://www.vulnhub.com/entry/acid-reloaded,127/",
        "https://www.vulnhub.com/entry/ai-web-1,353/",
        "https://www.vulnhub.com/entry/ai-web-2,357/",
        "https://www.vulnhub.com/entry/analougepond-1,185/",
        "https://www.vulnhub.com/entry/blacklight-1,242/",
        "https://www.vulnhub.com/entry/blackmarket-1,223/",
        "https://www.vulnhub.com/entry/bob-101,226/",
        "https://www.vulnhub.com/entry/bot-challenges-dexter,59/",
        "https://www.vulnhub.com/entry/breach-1,152/",
        "https://www.vulnhub.com/entry/breach-301,177/",
        "https://www.vulnhub.com/entry/casino-royale-1,287/",
        "https://www.vulnhub.com/entry/cengbox-1,475/",
        "https://www.vulnhub.com/entry/ch4inrulz-101,247/",
        "https://www.vulnhub.com/entry/clamp-101,320/",
        "https://www.vulnhub.com/entry/covfefe-1,199/",
        "https://www.vulnhub.com/entry/ctf-kfiofan-1,260/",
        "https://www.vulnhub.com/entry/ctf-kfiofan-2,325/",
        "https://www.vulnhub.com/entry/cynix-1,394/",
        "https://www.vulnhub.com/entry/d0not5top-12,191/",
        "https://www.vulnhub.com/entry/dc-4,313/",
        "https://www.vulnhub.com/entry/dc-5,314/",
        "https://www.vulnhub.com/entry/dc-6,315/",
        "https://www.vulnhub.com/entry/dc-7,356/",
        "https://www.vulnhub.com/entry/dc-8,367/",
        "https://www.vulnhub.com/entry/dc-9,412/",
        "https://www.vulnhub.com/entry/defence-space-ctf-2017,179/",
        "https://www.vulnhub.com/entry/de-ice-s1140,57/",
        "https://www.vulnhub.com/entry/depth-1,213/",
        "https://www.vulnhub.com/entry/derpnstink-1,221/",
        "https://www.vulnhub.com/entry/devrandom-pipe,124/",
        "https://www.vulnhub.com/entry/digitalworldlocal-bravery,281/",
        "https://www.vulnhub.com/entry/digitalworldlocal-development,280/",
        "https://www.vulnhub.com/entry/digitalworldlocal-joy,298/",
        "https://www.vulnhub.com/entry/digitalworldlocal-mercy-v2,263/",
        "https://www.vulnhub.com/entry/djinn-1,397/",
        "https://www.vulnhub.com/entry/domdom-1,328/",
        "https://www.vulnhub.com/entry/donkeydocker-1,189/",
        "https://www.vulnhub.com/entry/droopy-v02,143/",
        "https://www.vulnhub.com/entry/enubox-mattermost,414/",
        "https://www.vulnhub.com/entry/escalate_linux-1,323/",
        "https://www.vulnhub.com/entry/ew_skuzzy-1,184/",
        "https://www.vulnhub.com/entry/five86-1,417/",
        "https://www.vulnhub.com/entry/five86-2,418/",
        "https://www.vulnhub.com/entry/fristileaks-13,133/",
        "https://www.vulnhub.com/entry/gibson-02,146/",
        "https://www.vulnhub.com/entry/goldeneye-1,240/",
        "https://www.vulnhub.com/entry/hackademic-rtb2,18/",
        "https://www.vulnhub.com/entry/hackday-albania,167/",
        "https://www.vulnhub.com/entry/hackinos-1,295/",
        "https://www.vulnhub.com/entry/ha-infinity-stones,366/",
        "https://www.vulnhub.com/entry/happycorp-1,296/",
        "https://www.vulnhub.com/entry/inclusiveness-1,422/",
        "https://www.vulnhub.com/entry/jis-ctf-vulnupload,228/",
        "https://www.vulnhub.com/entry/kuya-1,283/",
        "https://www.vulnhub.com/entry/lampsecurity-ctf8,87/",
        "https://www.vulnhub.com/entry/linsecurity-1,244/",
        "https://www.vulnhub.com/entry/lord-of-the-root-101,129/",
        "https://www.vulnhub.com/entry/matrix-1,259/",
        "https://www.vulnhub.com/entry/matrix-2,279/",
        "https://www.vulnhub.com/entry/matrix-3,326/",
        "https://www.vulnhub.com/entry/minu-v2,333/",
        "https://www.vulnhub.com/entry/mission-pumpkin-v10-pumpkinraising,324/",
        "https://www.vulnhub.com/entry/mr-robot-1,151/",
        "https://www.vulnhub.com/entry/muzzybox-1,434/",
        "https://www.vulnhub.com/entry/nezuko-1,352/",
        "https://www.vulnhub.com/entry/node-1,252/",
        "https://www.vulnhub.com/entry/nullbyte-1,126/",
        "https://www.vulnhub.com/entry/pentester-lab-from-sql-injection-to-shell-ii,69/",
        "https://www.vulnhub.com/entry/pentester-lab-padding-oracle,174/",
        "https://www.vulnhub.com/entry/pinkys-palace-v1,225/",
        "https://www.vulnhub.com/entry/pwnlab-init,158/",
        "https://www.vulnhub.com/entry/raven-1,256/",
        "https://www.vulnhub.com/entry/rootthis-1,272/",
        "https://www.vulnhub.com/entry/rotating-fortress-101,248/",
        "https://www.vulnhub.com/entry/serial-1,349/",
        "https://www.vulnhub.com/entry/silky-ctf-0x01,306/",
        "https://www.vulnhub.com/entry/silky-ctf-0x02,307/",
        "https://www.vulnhub.com/entry/skydog-1,142/",
        "https://www.vulnhub.com/entry/skytower-1,96/",
        "https://www.vulnhub.com/entry/sp-ike-v101,275/",
        "https://www.vulnhub.com/entry/sp-jerome-v101,303/",
        "https://www.vulnhub.com/entry/spydersec-challenge,128/",
        "https://www.vulnhub.com/entry/stapler-1,150/",
        "https://www.vulnhub.com/entry/sunset-nightfall,355/",
        "https://www.vulnhub.com/entry/super-mario-host-101,186/",
        "https://www.vulnhub.com/entry/symfonos-1,322/",
        "https://www.vulnhub.com/entry/symfonos-2,331/",
        "https://www.vulnhub.com/entry/symfonos-31,332/",
        "https://www.vulnhub.com/entry/symfonos-4,347/",
        "https://www.vulnhub.com/entry/symfonos-52,415/",
        "https://www.vulnhub.com/entry/tbbt-2-funwithflags,461/",
        "https://www.vulnhub.com/entry/temple-of-doom-1,243/",
        "https://www.vulnhub.com/entry/the-beast-2,285/",
        "https://www.vulnhub.com/entry/the-ether-evilscience-v101,212/",
        "https://www.vulnhub.com/entry/the-library-1,334/",
        "https://www.vulnhub.com/entry/tommy-boy-1,157/",
        "https://www.vulnhub.com/entry/tophatsec-fartknocker,115/",
        "https://www.vulnhub.com/entry/tr0ll-1,100/",
        "https://www.vulnhub.com/entry/tr0ll-2,107/",
        "https://www.vulnhub.com/entry/tr0ll-3,340/",
        "https://www.vulnhub.com/entry/unknowndevice64-1,293/",
        "https://www.vulnhub.com/entry/usv-2016-v101,175/",
        "https://www.vulnhub.com/entry/vulnuni-101,439/",
        "https://www.vulnhub.com/entry/w1r3s-101,220/",
        "https://www.vulnhub.com/entry/w34kn3ss-1,270/",
        "https://www.vulnhub.com/entry/wakanda-1,251/",
        "https://www.vulnhub.com/entry/web-developer-1,288/",
        "https://www.vulnhub.com/entry/wintermute-1,239/",
        "https://www.vulnhub.com/entry/xerxes-1,58/",
        "https://www.vulnhub.com/entry/zeus-1,304/",
        "https://www.vulnhub.com/entry/zico2-1,210/",
      ],
      "hard": [ ## 40pts
        "https://www.vulnhub.com/entry/6days-lab-11,156/",
        "https://www.vulnhub.com/entry/billy-madison-11,161/",
        "https://www.vulnhub.com/entry/brainpan-1,51/",
        "https://www.vulnhub.com/entry/brainpan-2,56/",
        "https://www.vulnhub.com/entry/brainpan-3,121/",
        "https://www.vulnhub.com/entry/breach-1,152/",
        "https://www.vulnhub.com/entry/breach-21,159/",
        "https://www.vulnhub.com/entry/breach-301,177/",
        "https://www.vulnhub.com/entry/bulldog-2,246/",
        "https://www.vulnhub.com/entry/c0m80-1,198/",
        "https://www.vulnhub.com/entry/cyberry-1,217/",
        "https://www.vulnhub.com/entry/de-ice-s1130,11/",
        "https://www.vulnhub.com/entry/devrandom-k2,204/",
        "https://www.vulnhub.com/entry/digitalworldlocal-torment,299/",
        "https://www.vulnhub.com/entry/game-of-thrones-ctf-1,201/",
        "https://www.vulnhub.com/entry/gemini-inc-1,227/",
        "https://www.vulnhub.com/entry/gemini-inc-2,234/",
        "https://www.vulnhub.com/entry/hackerhouse-bsides-london-2017,202/",
        "https://www.vulnhub.com/entry/imf-1,162/",
        "https://www.vulnhub.com/entry/moonraker-1,264/",
        "https://www.vulnhub.com/entry/pinkys-palace-v2,229/",
        "https://www.vulnhub.com/entry/pinkys-palace-v3,237/",
        "https://www.vulnhub.com/entry/pinkys-palace-v4,265/",
        "https://www.vulnhub.com/entry/prime-1,358/",
        "https://www.vulnhub.com/entry/replay-1,278/",
        "https://www.vulnhub.com/entry/rop-primer-02,114/",
        "https://www.vulnhub.com/entry/skytower-1,96/",
        "https://www.vulnhub.com/entry/tempus-fugit-1,346/",
        "https://www.vulnhub.com/entry/teuchter-03,163/",
        "https://www.vulnhub.com/entry/the-necromancer-1,154/",
        "https://www.vulnhub.com/entry/the-wall-1,130/",
        "https://www.vulnhub.com/entry/trollcave-12,230/",
        "https://www.vulnhub.com/entry/usv-2017,219/",
        "https://www.vulnhub.com/entry/view2akill-1,387/",
        "https://www.vulnhub.com/entry/violator-1,153/",
        "https://www.vulnhub.com/entry/wintermute-1,239/",
      ],
      "insane": [],
    }

  def _get_all_machine_urls(self):
    # from timeline url, get machine urls
    machineurls = []
    res = utils.get_http_res("%s/timeline/" % self.baseurl)
    if res.status_code == 200 and res.text:
      pages = re.findall(r'<a href="/entry/[^"]+', res.text)
      if pages:
        machineurls = ["%s%s" % (self.baseurl, x.split('"', 2)[1].replace("/entry/", "entry/")) for x in pages]

    return machineurls

  def _parse_machine_page(self, url):
    if not url:
      return
    match = re.search(r'/entry/(.+),(\d+)/', url)
    if not match:
      return
    shortname, mid, url = match.groups()[0], int(match.groups()[1]), "https://www.vulnhub.com/entry/%s,%s/" % (match.groups()[0], match.groups()[1])
    machinestats = {
      "avatar_thumb": None,
      "id": mid,
      "maker": {
        "id": None,
        "name": None,
        "url": None,
      },
      "series": {
        "id": None,
        "name": None,
        "url": None,
      },
      "name": None,
      "shortname": shortname,
      "os": None,
      "points": None,
      "difficulty": None,
      "description": None,
      "release": None,
      "url": url,
    }
    res = utils.get_http_res(url)
    page = res.text

    soup = BeautifulSoup(page, 'lxml')
    container = soup.find('div', id="description", class_="panel")
    if not container:
      return machinestats

    machinestats["description"] = "\n".join([para.text for para in container.find_all('p', recursive=True)]).strip()

    # <li><b>Name</b>: Seppuku: 1</li>
    match = re.search(r'<li><b>Name</b>:\s*(.+)</li>', page, re.I)
    machinestats["name"] = utils.strip_html(match.groups()[0]) if match else None

    # <a href="/media/img/entry/
    match = re.search(r'<a href="/media/img/entry/([^"]+)', page, re.I)
    machinestats["avatar_thumb"] = "https://www.vulnhub.com/media/img/entry/%s" % (utils.strip_html(match.groups()[0])) if match else None

    # <li><b>Date release</b>: 13 May 2020</li>
    match = re.search(r'<li><b>Date release</b>:\s*(.+)</li>', page, re.I)
    machinestats["release"] = utils.strip_html(match.groups()[0]) if match else None

    # <li><b>Author</b>: <a href="/author/suncsr-team,696/">SunCSR Team</a></li>
    match = re.search(r'<li><b>Author</b>:\s*<a href="/author/(.+),(\d+)/">(.+)</a></li>', page, re.I)
    if match:
      machinestats["maker"]["name"] = utils.strip_html(match.groups()[2])
      machinestats["maker"]["id"] = int(utils.strip_html(match.groups()[1]))
      machinestats["maker"]["url"] = "https://www.vulnhub.com/author/%s,%s/" % (utils.strip_html(match.groups()[0]), utils.strip_html(match.groups()[1]))

    # <li><b>Series</b>: <a href="/series/seppuku,318/">Seppuku</a></li>
    match = re.search(r'<li><b>Series</b>:\s*<a href="/series/(.+),(\d+)/">(.+)</a></li>', page, re.I)
    if match:
      machinestats["series"]["name"] = utils.strip_html(match.groups()[2])
      machinestats["series"]["id"] = int(utils.strip_html(match.groups()[1]))
      machinestats["series"]["url"] = "https://www.vulnhub.com/series/%s,%s/" % (utils.strip_html(match.groups()[0]), utils.strip_html(match.groups()[1]))

    # <li><b>Operating System</b>: Linux</li>
    match = re.search(r'<li><b>Operating System</b>:\s*(.+)</li>', page, re.I)
    machinestats["os"] = utils.strip_html(match.groups()[0]) if match else None

    if machinestats["url"] in self.difficulty["easy"]:
      machinestats["difficulty"] = "easy"
    elif machinestats["url"] in self.difficulty["medium"]:
      machinestats["difficulty"] = "medium"
    elif machinestats["url"] in self.difficulty["hard"]:
      machinestats["difficulty"] = "hard"
    elif machinestats["url"] in self.difficulty["insane"]:
      machinestats["difficulty"] = "insane"

    if not machinestats["difficulty"]:
      # <li>Difficulty: Intermediate to Hard</li>
      # <li>Difficulty: <strong>Beginner to Intermediate</strong></li>
      match = re.search(r'<li>Difficulty\s*:\s*(<strong>)?(.+)(</strong>)?</li>', page, re.I)
      machinestats["difficulty"] = utils.strip_html(match.groups()[1]) if match else None

    if not machinestats["difficulty"]:
      # <p>Difficulty is Medium</p>
      # <p>Difficulty: Intermediate
      # <p>Difficulty : beginner/intermediate</p>
      # <p>Level : beginner for user flag and intermediate for root flag.</p>
      match = re.search(r'<p>(Difficulty|Level)\s*(is|:)\s*(.+)</p>', page, re.I)
      machinestats["difficulty"] = utils.strip_html(match.groups()[2]) if match else None

    if not machinestats["difficulty"]:
      # An easy to intermediate boot2root
      match = re.search(r'easy\s+(to|/)\s+intermediate', page, re.I)
      machinestats["difficulty"] = "Easy/Intermediate" if match else None

    if not machinestats["difficulty"]:
      # beginner boot2root
      match = re.search(r'(beginner\s+boot2root|A piece of cake machine)', page, re.I)
      machinestats["difficulty"] = "Easy" if match else None

    if not machinestats["difficulty"]:
      # medium level difficulty
      match = re.search(r'(medium\s+level\s+difficulty)', page, re.I)
      machinestats["difficulty"] = "Medium" if match else None

    if not machinestats["difficulty"]:
      # <p>[BEGINNER - INTERMEDIATE]</p>
      # beginner to intermediate boot2root
      match = re.search(r'BEGINNER\s*(-|to)?\s*INTERMEDIATE', page, re.I)
      machinestats["difficulty"] = "Beginner/Intermediate" if match else None

    if machinestats["difficulty"]:
      mapping = {
        "insane": ["insane"],
        "hard": ["hard", "difficult", "challenging", "intermediate++"],
        "medium": ["medium", "intermediate", "moderate", "beginner++"],
        "easy": ["easy", "beginner", "low"],
      }

      newdiff = None
      for normdiff in mapping["insane"]:
        if normdiff in machinestats["difficulty"].lower().strip():
          newdiff = "insane"
          break
      if not newdiff:
        for normdiff in mapping["hard"]:
          if normdiff in machinestats["difficulty"].lower().strip():
            newdiff = "hard"
            break
      if not newdiff:
        for normdiff in mapping["medium"]:
          if normdiff in machinestats["difficulty"].lower().strip():
            newdiff = "medium"
            break
      if not newdiff:
        for normdiff in mapping["easy"]:
          if normdiff in machinestats["difficulty"].lower().strip():
            newdiff = "easy"
            break

      machinestats["difficulty"] = newdiff if newdiff else None
      machinestats["points"] = None

    return machinestats

  def get_all_machine_stats(self, ctfdiffupdate=True):
    machineurls = self._get_all_machine_urls()
    machines = []
    for url in machineurls:
      stats = self._parse_machine_page(url)
      if stats:
        machines.append(stats)
    return machines

  def get_machine_stats(self, url):
    stats = self._parse_machine_page(url)
    if stats:
      return stats
