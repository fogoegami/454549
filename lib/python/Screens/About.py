import boxbranding
try:
	import urllib2
except ImportError:
	import urllib

from enigma import eConsoleAppContainer, eDVBResourceManager, eGetEnigmaDebugLvl, eLabel, eTimer, getBoxType, getDesktop, getE2Rev
from os import listdir, popen, remove
from os.path import getmtime, isfile, join as pathjoin
from six import PY2, PY3, ensure_str as ensurestr, text_type as texttype

import skin, os, re, urllib2, sys, boxbranding
from skin import parameters
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.config import config
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.Harddisk import harddiskmanager, Harddisk
from Components.NimManager import nimmanager
from Components.About import about
from Components.ScrollLabel import ScrollLabel
from Components.Button import Button
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from Tools.StbHardware import getFPVersion, getBoxProc
from Components.Pixmap import MultiPixmap
from Components.Network import iNetwork
from Components.SystemInfo import SystemInfo
from re import search
from Tools.Directories import fileExists, fileHas, pathExists
from Components.GUIComponent import GUIComponent
from Components.Console import Console
from Tools.Geolocation import geolocation

URL ='https://raw.githubusercontent.com/norhap/enigma2-openvision-1/develop/NEWS'

def news(url):
    text = ""
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        link = response.read().decode("windows-1252")
        response.close()
        text = link.encode("utf-8")

    except:
        print("ERROR novedades alvaro %s" %(url))

    return text

class About(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("About"))
		self["lab1"] = StaticText(_("OpenVision"))
		self["lab2"] = StaticText(_("Lets define enigma2 once more"))
		self["lab3"] = StaticText(_("Report problems to:"))
		self["lab4"] = StaticText(_("https://openvision.tech"))
		self["lab5"] = StaticText(_("Sources are available at:"))
		self["lab6"] = StaticText(_("https://github.com/OpenVisionE2"))
		hddsplit = skin.parameters.get("AboutHddSplit", 0)

		procmodel = getBoxProc()

		AboutText = _("Hardware: ") + about.getHardwareTypeString() + "\n"
		if procmodel != about.getHardwareTypeString():
			AboutText += _("Modelo: ") + procmodel + "\n"
		if fileExists("/proc/stb/info/sn"):
			hwserial = open("/proc/stb/info/sn", "r").read().strip()
			AboutText += _("Hardware serial: ") + hwserial + "\n"

		AboutText += _("Fabricante: ") + about.getHardwareBrand() + "\n"

		cpu = about.getCPUInfoString()
		AboutText += _("CPU: ") + cpu + "\n"
		AboutText += _("Fabricante CPU: ") + about.getCPUBrand() + "\n"
		AboutText += _("CPU Arquitectura: ") + about.getCPUArch() + "\n"
		AboutText += _("Flash tipo: ") + about.getFlashType() + "\n"
		AboutText += _("Image: ") + about.getImageTypeString() + "\n"
		AboutText += _("Build date: ") + about.getBuildDateString() + "\n"
		AboutText += _("Last update: ") + about.getUpdateDateString() + "\n"

		# [WanWizard] Removed until we find a reliable way to determine the installation date
		# AboutText += _("Installed: ") + about.getFlashDateString() + "\n"

		EnigmaVersion = about.getEnigmaVersionString()
		EnigmaVersion = EnigmaVersion.rsplit("-", EnigmaVersion.count("-") - 2)
		if len(EnigmaVersion) == 3:
			EnigmaVersion = EnigmaVersion[0] + " (" + EnigmaVersion[2] + "-" + EnigmaVersion[1] + ")"
		else:
			EnigmaVersion = EnigmaVersion[0] + " (" + EnigmaVersion[1] + ")"
		EnigmaVersion = _("Enigma version: ") + EnigmaVersion
		self["EnigmaVersion"] = StaticText(EnigmaVersion)
		AboutText += "\n" + EnigmaVersion + "\n"
		AboutText += _("Enigma2 revision: ") + getE2Rev() + "\n"
		AboutText += _("Last update: ") + about.getUpdateDateString() + "\n"
		AboutText += _("Enigma2 (re)starts: %d\n") % config.misc.startCounter.value
		AboutText += _("Enigma2 debug level: %d\n") % eGetEnigmaDebugLvl()

		AboutText += _("Kernel version: ") + about.getKernelVersionString() + "\n"

		AboutText += _("DVB driver version: ") + about.getDriverInstalledDate() + "\n"

		numSlots = 0
		dvbinformation = ""
		nimSlots = nimmanager.getSlotCount()
		for nim in range(nimSlots):
			dvbinformation += eDVBResourceManager.getInstance().getFrontendCapabilities(nim)

		dvbapiversion = ""
		dvbapiversion = dvbinformation.splitlines()[0].replace("DVB API version: ", "").strip()
		AboutText += _("DVB API version: ") + dvbapiversion + "\n"

		if fileExists("/usr/bin/dvb-fe-tool"):
			import time
			try:
				cmd = 'dvb-fe-tool > /tmp/dvbfetool.txt ; dvb-fe-tool -f 1 >> /tmp/dvbfetool.txt ; cat /proc/bus/nim_sockets >> /tmp/dvbfetool.txt'
				res = Console().ePopen(cmd)
				time.sleep(0.1)
			except:
				pass

		if "MULTISTREAM" in dvbinformation:
			AboutText += _("Multistream: ") + _("Yes") + "\n"
		else:
			AboutText += _("Multistream: ") + _("No") + "\n"
		if fileExists("/tmp/dvbfetool.txt"):
			if fileHas("/tmp/dvbfetool.txt","DVB-S2X") or pathExists("/proc/stb/frontend/0/t2mi") or pathExists("/proc/stb/frontend/1/t2mi"):
				AboutText += _("DVB-S2X: ") + _("Yes") + "\n"
			if fileHas("/tmp/dvbfetool.txt","DVBS2") or fileHas("/tmp/dvbfetool.txt","DVB-S") or fileHas("/var/log/dmesg","DVB-S2"):
				AboutText += _("DVB-S/S2: ") + _("Yes") + "\n"
			if fileHas("/tmp/dvbfetool.txt","Mode 2: DVB-S"):
				AboutText += _("DVB-S2/T2/C: ") + _("Yes") + "\n"
			if fileHas("/tmp/dvbfetool.txt","DVB-T2") or fileHas("/tmp/dvbfetool.txt","DVBT"):
				AboutText += _("DVB-T2/C: ") + _("Yes") + "\n"
			if fileHas("/tmp/dvbfetool.txt","DVB-C") and not fileHas("/tmp/dvbfetool.txt","DVB-T2"):
				AboutText += _("DVB-Cable: ") + _("Yes") + "\n"
			if "DVBC_ANNEX_A" in dvbinformation:
				AboutText += _("DVBC_ANNEX_A: ") + _("Yes") + "\n"
			if "DVBC_ANNEX_B"  in dvbinformation:
				AboutText += _("DVBC_ANNEX_B: ") + _("Yes") + "\n"
			if "DVBC_ANNEX_C"  in dvbinformation:
				AboutText += _("DVBC_ANNEX_C: ") + _("Yes") + "\n"

		GStreamerVersion = _("GStreamer version: ") + about.getGStreamerVersionString(cpu).replace("GStreamer","")
		self["GStreamerVersion"] = StaticText(GStreamerVersion)
		AboutText += GStreamerVersion + "\n"

		FFmpegVersion = _("FFmpeg version: ") + about.getFFmpegVersionString()
		self["FFmpegVersion"] = StaticText(FFmpegVersion)
		AboutText += FFmpegVersion + "\n"

		AboutText += _("Python version: ") + about.getPythonVersionString() + "\n"

		AboutText += _("Enigma (re)starts: %d\n") % config.misc.startCounter.value
		AboutText += _("Enigma debug level: %d\n") % eGetEnigmaDebugLvl()

		fp_version = getFPVersion()
		if fp_version is None:
			fp_version = ""
		else:
			fp_version = _("Frontprocessor version: %s") % fp_version
			AboutText += fp_version + "\n"

		self["FPVersion"] = StaticText(fp_version)

		if fileExists("/var/lib/opkg/info/enigma2-plugin-systemplugins-transcodingsetup.list"):
			AboutText += _("Setup Transcoding: ") + _("Yes") + "\n"
		else:
			AboutText += _("Setup Transcoding: ") + _("No") + "\n"
		if fileExists("/var/lib/opkg/info/enigma2-plugin-systemplugins-multitranscodingsetup.list"):
			AboutText += _("Setup MultiTranscoding: ") + _("Yes") + "\n"
		else:
			AboutText += _("Setup MultiTranscoding: ") + _("No") + "\n"

		AboutText += _('Skin & Resolution: %s (%sx%s)\n') % (config.skin.primary_skin.value.split('/')[0], getDesktop(0).size().width(), getDesktop(0).size().height())

		self["TunerHeader"] = StaticText(_("Detected NIMs:"))
		AboutText += "\n" + _("Detected NIMs:") + "\n"

		nims = nimmanager.nimListCompressed()
		for count in range(len(nims)):
			if count < 4:
				self["Tuner" + str(count)] = StaticText(nims[count])
			else:
				self["Tuner" + str(count)] = StaticText("")
			AboutText += nims[count] + "\n"

		self["HDDHeader"] = StaticText(_("Detected HDD:"))
		AboutText += "\n" + _("Detected HDD:") + "\n"

		hddlist = harddiskmanager.HDDList()
		hddinfo = ""
		if hddlist:
			formatstring = hddsplit and "%s:%s, %.1f %sB %s" or "%s\n(%s, %.1f %sB %s)"
			for count in range(len(hddlist)):
				if hddinfo:
					hddinfo += "\n"
				hdd = hddlist[count][1]
				if int(hdd.free()) > 1024:
					hddinfo += formatstring % (hdd.model(), hdd.capacity(), hdd.Totalfree()/1024.0, "G", _("free"))
				else:
					hddinfo += formatstring % (hdd.model(), hdd.capacity(), hdd.Totalfree(), "M", _("free"))
		else:
			hddinfo = _("none")
		self["hddA"] = StaticText(hddinfo)
		AboutText += hddinfo + "\n\n" + _("Network Info:")
		for x in about.GetIPsFromNetworkInterfaces():
			AboutText += "\n" + x[0] + ": " + x[1]
		AboutText += '\n\n' + _("Uptime:") + "  " + about.getBoxUptime()

		self["AboutScrollLabel"] = ScrollLabel(AboutText)
		self["key_green"] = Button(_("Translations"))
		self["key_red"] = Button(_("Latest Commits"))
		self["key_yellow"] = Button(_("Dmesg Info"))
		self["key_blue"] = Button(_("Memory Info"))

		self["actions"] = ActionMap(["OkCancelActions", "SetupActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"red": self.showCommits,
				"green": self.showTranslationInfo,
				"blue": self.showMemoryInfo,
				"yellow": self.showTroubleshoot,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			})

	def showTranslationInfo(self):
		self.session.open(TranslationInfo)

	def showCommits(self):
		self.session.open(CommitInfoDevelop)

	def showMemoryInfo(self):
		self.session.open(MemoryInfo)

	def showTroubleshoot(self):
		self.session.open(Troubleshoot)

class Geolocation(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Geolocation"))
		self.setTitle(_("Open Vision information"))
		self["lab1"] = StaticText(_("OpenVision"))
		self["lab2"] = StaticText(_("Lets define enigma2 once more"))
		self["lab3"] = StaticText(_("Report problems to:"))
		self["lab4"] = StaticText(_("https://openvision.tech"))
		self["lab5"] = StaticText(_("Sources are available at:"))
		self["lab6"] = StaticText(_("https://github.com/OpenVisionE2"))

		GeolocationText = _("Geolocation information") + "\n"

		GeolocationText += "\n"

		try:
			geolocationData = geolocation.getGeolocationData(fields="continent,country,regionName,city,timezone,currency,lat,lon", useCache=True)
			continent = geolocationData.get("continent", None)
			if isinstance(continent, texttype):
				continent = ensurestr(continent.encode(encoding="UTF-8", errors="ignore"))
			if continent is not None:
				GeolocationText += _("Continent: ") + continent + "\n"

			country = geolocationData.get("country", None)
			if isinstance(country, texttype):
				country = ensurestr(country.encode(encoding="UTF-8", errors="ignore"))
			if country is not None:
				GeolocationText += _("Country: ") + country + "\n"

			state = geolocationData.get("regionName", None)
			if isinstance(state, texttype):
				state = ensurestr(state.encode(encoding="UTF-8", errors="ignore"))
			if state is not None:
				GeolocationText += _("State: ") + state + "\n"

			city = geolocationData.get("city", None)
			if isinstance(city, texttype):
				city = ensurestr(city.encode(encoding="UTF-8", errors="ignore"))
			if city is not None:
				GeolocationText += _("City: ") + city + "\n"

			GeolocationText += "\n"

			timezone = geolocationData.get("timezone", None)
			if isinstance(timezone, texttype):
				timezone = ensurestr(timezone.encode(encoding="UTF-8", errors="ignore"))
			if timezone is not None:
				GeolocationText += _("Timezone: ") + timezone + "\n"

			currency = geolocationData.get("currency", None)
			if isinstance(currency, texttype):
				currency = ensurestr(currency.encode(encoding="UTF-8", errors="ignore"))
			if currency is not None:
				GeolocationText += _("Currency: ") + currency + "\n"

			GeolocationText += "\n"

			latitude = geolocationData.get("lat", None)
			if str(float(latitude)) is not None:
				GeolocationText += _("Latitude: ") + str(float(latitude)) + "\n"

			longitude = geolocationData.get("lon", None)
			if str(float(longitude)) is not None:
				GeolocationText += _("Longitude: ") + str(float(longitude)) + "\n"
			self["AboutScrollLabel"] = ScrollLabel(GeolocationText)
		except Exception as err:
			self["AboutScrollLabel"] = ScrollLabel(_("Requires internet connection"))

		self["key_red"] = Button(_("Close"))

		self["actions"] = ActionMap(["ColorActions", "SetupActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			})

class Devices(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		screentitle = _("Devices")
		title = screentitle
		Screen.setTitle(self, title)
		self["TunerHeader"] = StaticText(_("Detected tuners:"))
		self["HDDHeader"] = StaticText(_("Detected devices:"))
		self["MountsHeader"] = StaticText(_("Network servers:"))
		self["nims"] = StaticText()
		self["lab1"] = StaticText(_("OpenVision"))
		self["lab2"] = StaticText(_("Lets define enigma2 once more"))
		self["lab3"] = StaticText(_("Report problems to:"))
		self["lab4"] = StaticText(_("https://openvision.tech"))
		self["lab5"] = StaticText(_("Sources are available at:"))
		self["lab6"] = StaticText(_("https://github.com/OpenVisionE2"))
		for count in (0, 1, 2, 3):
			self["Tuner" + str(count)] = StaticText("")
		self["hdd"] = StaticText()
		self["mounts"] = StaticText()
		self.list = []
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.populate2)
		self["key_red"] = Button(_("Close"))
		self["actions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
									{
										"cancel": self.close,
										"ok": self.close,
										"red": self.close,
									})
		self.onLayoutFinish.append(self.populate)

	def populate(self):
		self.mountinfo = ''
		self["actions"].setEnabled(False)
		scanning = _("Please wait while scanning for devices...")
		self["nims"].setText(scanning)
		for count in (0, 1, 2, 3):
			self["Tuner" + str(count)].setText(scanning)
		self["hdd"].setText(scanning)
		self['mounts'].setText(scanning)
		self.activityTimer.start(1)

	def populate2(self):
		self.activityTimer.stop()
		self.Console = Console()
		niminfo = ""
		nims = nimmanager.nimListCompressed()
		for count in range(len(nims)):
			if niminfo:
				niminfo += "\n"
			niminfo += nims[count]
		self["nims"].setText(niminfo)

		nims = nimmanager.nimList()
		if len(nims) <= 4 :
			for count in (0, 1, 2, 3):
				if count < len(nims):
					self["Tuner" + str(count)].setText(nims[count])
				else:
					self["Tuner" + str(count)].setText("")
		else:
			desc_list = []
			count = 0
			cur_idx = -1
			while count < len(nims):
				data = nims[count].split(":")
				idx = data[0].strip('Tuner').strip()
				desc = data[1].strip()
				if desc_list and desc_list[cur_idx]['desc'] == desc:
					desc_list[cur_idx]['end'] = idx
				else:
					desc_list.append({'desc' : desc, 'start' : idx, 'end' : idx})
					cur_idx += 1
				count += 1

			for count in (0, 1, 2, 3):
				if count < len(desc_list):
					if desc_list[count]['start'] == desc_list[count]['end']:
						text = "Tuner %s: %s" % (desc_list[count]['start'], desc_list[count]['desc'])
					else:
						text = "Tuner %s-%s: %s" % (desc_list[count]['start'], desc_list[count]['end'], desc_list[count]['desc'])
				else:
					text = ""

				self["Tuner" + str(count)].setText(text)

		self.hddlist = harddiskmanager.HDDList()
		self.list = []
		if self.hddlist:
			for count in range(len(self.hddlist)):
				hdd = self.hddlist[count][1]
				hddp = self.hddlist[count][0]
				if "ATA" in hddp:
					hddp = hddp.replace('ATA', '')
					hddp = hddp.replace('Internal', 'ATA Bus ')
				free = hdd.Totalfree()
				if ((float(free) / 1024) / 1024) >= 1:
					freeline = _("Free: ") + str(round(((float(free) / 1024) / 1024), 2)) + _("TB")
				elif (free / 1024) >= 1:
					freeline = _("Free: ") + str(round((float(free) / 1024), 2)) + _("GB")
				elif free >= 1:
					freeline = _("Free: ") + str(free) + _("MB")
				elif "Generic(STORAGE" in hddp:
					continue
				else:
					freeline = _("Free: ") + _("full")
				line = "%s      %s" %(hddp, freeline)
				self.list.append(line)
		self.list = '\n'.join(self.list)
		self["hdd"].setText(self.list)

		self.Console.ePopen("df -mh | grep -v '^Filesystem'", self.Stage1Complete)

	def Stage1Complete(self, result, retval, extra_args=None):
		if PY2:
			result = result.replace('\n                        ', ' ').split('\n')
		else:
			result = result.decode().replace('\n                        ', ' ').split('\n')
		self.mountinfo = ""
		for line in result:
			self.parts = line.split()
			if line and self.parts[0] and (self.parts[0].startswith('192') or self.parts[0].startswith('//192')):
				line = line.split()
				ipaddress = line[0]
				mounttotal = line[1]
				mountfree = line[3]
				if self.mountinfo:
					self.mountinfo += "\n"
				self.mountinfo += "%s (%sB, %sB %s)" % (ipaddress, mounttotal, mountfree, _("free"))
		if pathExists("/media/autofs"):
			for entry in sorted(listdir("/media/autofs")):
				mountEntry = path.join("/media/autofs", entry)
				self.mountinfo += _("\n %s " % (mountEntry))

		if self.mountinfo:
			self["mounts"].setText(self.mountinfo)
		else:
			self["mounts"].setText(_('none'))
		self["actions"].setEnabled(True)

class SystemNetworkInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		screentitle = _("Network")
		title = screentitle
		Screen.setTitle(self, title)
		self.skinName = ["SystemNetworkInfo", "WlanStatus"]
		self["LabelBSSID"] = StaticText()
		self["LabelESSID"] = StaticText()
		self["LabelQuality"] = StaticText()
		self["LabelSignal"] = StaticText()
		self["LabelBitrate"] = StaticText()
		self["LabelEnc"] = StaticText()
		self["BSSID"] = StaticText()
		self["ESSID"] = StaticText()
		self["quality"] = StaticText()
		self["signal"] = StaticText()
		self["bitrate"] = StaticText()
		self["enc"] = StaticText()
		self["lab1"] = StaticText(_("OpenVision"))
		self["lab2"] = StaticText(_("Lets define enigma2 once more"))
		self["lab3"] = StaticText(_("Report problems to:"))
		self["lab4"] = StaticText(_("https://openvision.tech"))
		self["lab5"] = StaticText(_("Sources are available at:"))
		self["lab6"] = StaticText(_("https://github.com/OpenVisionE2"))

		self["IFtext"] = StaticText()
		self["IF"] = StaticText()
		self["Statustext"] = StaticText()
		self["statuspic"] = MultiPixmap()
		self["statuspic"].setPixmapNum(1)
		self["statuspic"].show()
		self["devicepic"] = MultiPixmap()

		self["AboutScrollLabel"] = ScrollLabel()

		self.iface = None
		self.createscreen()
		self.iStatus = None

		if iNetwork.isWirelessInterface(self.iface):
			try:
				from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus

				self.iStatus = iStatus
			except:
				pass
			self.resetList()
			self.onClose.append(self.cleanup)

		self["key_red"] = StaticText(_("Close"))

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
									{
										"cancel": self.close,
										"ok": self.close,
										"up": self["AboutScrollLabel"].pageUp,
										"down": self["AboutScrollLabel"].pageDown
									})
		self.onLayoutFinish.append(self.updateStatusbar)

	def createscreen(self):
		self.AboutText = ""
		self.iface = "eth0"
		eth0 = about.getIfConfig('eth0')
		if 'addr' in eth0:
			self.AboutText += _("IP:") + "\t" + eth0['addr'] + "\n"
			if 'netmask' in eth0:
				self.AboutText += _("Netmask:") + "\t" + eth0['netmask'] + "\n"
			if 'hwaddr' in eth0:
				self.AboutText += _("MAC:") + "\t" + eth0['hwaddr'] + "\n"
			self.iface = 'eth0'

		eth1 = about.getIfConfig('eth1')
		if 'addr' in eth1:
			self.AboutText += _("IP:") + "\t" + eth1['addr'] + "\n"
			if 'netmask' in eth1:
				self.AboutText += _("Netmask:") + "\t" + eth1['netmask'] + "\n"
			if 'hwaddr' in eth1:
				self.AboutText += _("MAC:") + "\t" + eth1['hwaddr'] + "\n"
			self.iface = 'eth1'

		ra0 = about.getIfConfig('ra0')
		if 'addr' in ra0:
			self.AboutText += _("IP:") + "\t" + ra0['addr'] + "\n"
			if 'netmask' in ra0:
				self.AboutText += _("Netmask:") + "\t" + ra0['netmask'] + "\n"
			if 'hwaddr' in ra0:
				self.AboutText += _("MAC:") + "\t" + ra0['hwaddr'] + "\n"
			self.iface = 'ra0'

		wlan0 = about.getIfConfig('wlan0')
		if 'addr' in wlan0:
			self.AboutText += _("IP:") + "\t" + wlan0['addr'] + "\n"
			if 'netmask' in wlan0:
				self.AboutText += _("Netmask:") + "\t" + wlan0['netmask'] + "\n"
			if 'hwaddr' in wlan0:
				self.AboutText += _("MAC:") + "\t" + wlan0['hwaddr'] + "\n"
			self.iface = 'wlan0'

		wlan3 = about.getIfConfig('wlan3')
		if 'addr' in wlan3:
			self.AboutText += _("IP:") + "\t" + wlan3['addr'] + "\n"
			if 'netmask' in wlan3:
				self.AboutText += _("Netmask:") + "\t" + wlan3['netmask'] + "\n"
			if 'hwaddr' in wlan3:
				self.AboutText += _("MAC:") + "\t" + wlan3['hwaddr'] + "\n"
			self.iface = 'wlan3'

		rx_bytes, tx_bytes = about.getIfTransferredData(self.iface)
		self.AboutText += "\n" + _("Bytes received:") + "\t" + rx_bytes + "\n"
		self.AboutText += _("Bytes sent:") + "\t" + tx_bytes + "\n"

		geolocationData = geolocation.getGeolocationData(fields="isp,org,mobile,proxy,query", useCache=True)
		isp = geolocationData.get("isp", None)
		isporg = geolocationData.get("org", None)
		if isinstance(isp, texttype):
			isp = ensurestr(isp.encode(encoding="UTF-8", errors="ignore"))
		if isinstance(isporg, texttype):
			isporg = ensurestr(isporg.encode(encoding="UTF-8", errors="ignore"))
		self.AboutText += "\n"
		if isp is not None:
			if isporg is not None:
				self.AboutText += _("ISP: ") + isp + " " + "(" + isporg + ")" + "\n"
			else:
				self.AboutText +=  "\n" + _("ISP: ") + isp + "\n"

		mobile = geolocationData.get("mobile", False)
		if mobile is not False:
			self.AboutText += _("Mobile: ") + _("Yes") + "\n"
		else:
			self.AboutText += _("Mobile: ") + _("No") + "\n"

		proxy = geolocationData.get("proxy", False)
		if proxy is not False:
			self.AboutText += _("Proxy: ") + _("Yes") + "\n"
		else:
			self.AboutText += _("Proxy: ") + _("No") + "\n"

		publicip = geolocationData.get("query", None)
		if str(publicip) != "":
			self.AboutText +=  _("Public IP: ") + str(publicip) + "\n" + "\n"

		self.console = Console()
		self.console.ePopen('ethtool %s' % self.iface, self.SpeedFinished)

	def SpeedFinished(self, result, retval, extra_args):
		if PY2:
			result_tmp = result.split('\n')
		else:
			result_tmp = result.decode().split('\n')
		for line in result_tmp:
			if 'Speed:' in line:
				speed = line.split(': ')[1][:-4]
				self.AboutText += _("Speed:") + "\t" + speed + _('Mb/s')

		hostname = file('/proc/sys/kernel/hostname').read()
		self.AboutText += "\n" + _("Hostname:") + "\t" + hostname + "\n"
		self["AboutScrollLabel"].setText(self.AboutText)

	def cleanup(self):
		if self.iStatus:
			self.iStatus.stopWlanConsole()

	def resetList(self):
		if self.iStatus:
			self.iStatus.getDataForInterface(self.iface, self.getInfoCB)

	def getInfoCB(self, data, status):
		self.LinkState = None
		if data is not None and data:
			if status is not None:
# getDataForInterface()->iwconfigFinished() in
# Plugins/SystemPlugins/WirelessLan/Wlan.py sets fields to boolean False
# if there is no info for them, so we need to check that possibility
# for each status[self.iface] field...
#
				if self.iface == 'wlan0' or self.iface == 'wlan3' or self.iface == 'ra0':
# accesspoint is used in the "enc" code too, so we get it regardless
#
					if not status[self.iface]["accesspoint"]:
						accesspoint = _("Unknown")
					else:
						if status[self.iface]["accesspoint"] == "Not-Associated":
							accesspoint = _("Not-Associated")
							essid = _("No connection")
						else:
							accesspoint = status[self.iface]["accesspoint"]
					if 'BSSID' in self:
						self.AboutText += _('Accesspoint:') + '\t' + accesspoint + '\n'

					if 'ESSID' in self:
						if not status[self.iface]["essid"]:
							essid = _("Unknown")
						else:
							if status[self.iface]["essid"] == "off":
								essid = _("No connection")
							else:
								essid = status[self.iface]["essid"]
						self.AboutText += _('SSID:') + '\t' + essid + '\n'

					if 'quality' in self:
						if not status[self.iface]["quality"]:
							quality = _("Unknown")
						else:
							quality = status[self.iface]["quality"]
						self.AboutText += _('Link quality:') + '\t' + quality + '\n'

					if 'bitrate' in self:
						if not status[self.iface]["bitrate"]:
							bitrate = _("Unknown")
						else:
							if status[self.iface]["bitrate"] == '0':
								bitrate = _("Unsupported")
							else:
								bitrate = str(status[self.iface]["bitrate"]) + " Mb/s"
						self.AboutText += _('Bitrate:') + '\t' + bitrate + '\n'

					if 'signal' in self:
						if not status[self.iface]["signal"]:
							signal = _("Unknown")
						else:
							signal = status[self.iface]["signal"]
						self.AboutText += _('Signal strength:') + '\t' + signal + '\n'

					if 'enc' in self:
						if not status[self.iface]["encryption"]:
							encryption = _("Unknown")
						else:
							if status[self.iface]["encryption"] == "off":
								if accesspoint == "Not-Associated":
									encryption = _("Disabled")
								else:
									encryption = _("Unsupported")
							else:
								encryption = _("Enabled")
						self.AboutText += _('Encryption:') + '\t' + encryption + '\n'

					if ((status[self.iface]["essid"] and status[self.iface]["essid"] == "off") or
					    not status[self.iface]["accesspoint"] or
					    status[self.iface]["accesspoint"] == "Not-Associated"):
						self.LinkState = False
						self["statuspic"].setPixmapNum(1)
						self["statuspic"].show()
					else:
						self.LinkState = True
						iNetwork.checkNetworkState(self.checkNetworkCB)
					self["AboutScrollLabel"].setText(self.AboutText)

	def exit(self):
		self.close(True)

	def updateStatusbar(self):
		self["IFtext"].setText(_("Network:"))
		self["IF"].setText(iNetwork.getFriendlyAdapterName(self.iface))
		self["Statustext"].setText(_("Link:"))
		if iNetwork.isWirelessInterface(self.iface):
			self["devicepic"].setPixmapNum(1)
			try:
				self.iStatus.getDataForInterface(self.iface, self.getInfoCB)
			except:
				self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
		else:
			iNetwork.getLinkState(self.iface, self.dataAvail)
			self["devicepic"].setPixmapNum(0)
		self["devicepic"].show()

	def dataAvail(self, data):
		if PY3:
			data = data.decode()
		self.LinkState = None
		for line in data.splitlines():
			line = line.strip()
			if 'Link detected:' in line:
				if "yes" in line:
					self.LinkState = True
				else:
					self.LinkState = False
		if self.LinkState:
			iNetwork.checkNetworkState(self.checkNetworkCB)
		else:
			self["statuspic"].setPixmapNum(1)
			self["statuspic"].show()

	def checkNetworkCB(self, data):
		try:
			if iNetwork.getAdapterAttribute(self.iface, "up") is True:
				if self.LinkState is True:
					if data <= 2:
						self["statuspic"].setPixmapNum(0)
					else:
						self["statuspic"].setPixmapNum(1)
				else:
					self["statuspic"].setPixmapNum(1)
			else:
				self["statuspic"].setPixmapNum(1)
			self["statuspic"].show()
		except:
			pass

class SystemMemoryInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		screentitle = _("Memory")
		title = screentitle
		Screen.setTitle(self, title)
		self.skinName = ["SystemMemoryInfo", "About"]
		self["lab1"] = StaticText(_("OpenVision"))
		self["lab2"] = StaticText(_("Lets define enigma2 once more"))
		self["lab3"] = StaticText(_("Report problems to:"))
		self["lab4"] = StaticText(_("https://openvision.tech"))
		self["lab5"] = StaticText(_("Sources are available at:"))
		self["lab6"] = StaticText(_("https://github.com/OpenVisionE2"))
		self["AboutScrollLabel"] = ScrollLabel()

		self["key_red"] = Button(_("Close"))
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
									{
										"cancel": self.close,
										"ok": self.close,
										"red": self.close,
									})

		out_lines = file("/proc/meminfo").readlines()
		self.AboutText = _("RAM") + '\n\n'
		RamTotal = "-"
		RamFree = "-"
		for lidx in range(len(out_lines) - 1):
			tstLine = out_lines[lidx].split()
			if "MemTotal:" in tstLine:
				MemTotal = out_lines[lidx].split()
				self.AboutText += _("Total memory:") + "\t" + MemTotal[1] + "\n"
			if "MemFree:" in tstLine:
				MemFree = out_lines[lidx].split()
				self.AboutText += _("Free memory:") + "\t" + MemFree[1] + "\n"
			if "Buffers:" in tstLine:
				Buffers = out_lines[lidx].split()
				self.AboutText += _("Buffers:") + "\t" + Buffers[1] + "\n"
			if "Cached:" in tstLine:
				Cached = out_lines[lidx].split()
				self.AboutText += _("Cached:") + "\t" + Cached[1] + "\n"
			if "SwapTotal:" in tstLine:
				SwapTotal = out_lines[lidx].split()
				self.AboutText += _("Total swap:") + "\t" + SwapTotal[1] + "\n"
			if "SwapFree:" in tstLine:
				SwapFree = out_lines[lidx].split()
				self.AboutText += _("Free swap:") + "\t" + SwapFree[1] + "\n\n"

		self["actions"].setEnabled(False)
		self.Console = Console()
		self.Console.ePopen("df -mh / | grep -v '^Filesystem'", self.Stage1Complete2)

	def Stage1Complete2(self, result, retval, extra_args=None):
		flash = str(result).replace('\n', '')
		flash = flash.split()
		RamTotal = flash[1]
		RamFree = flash[3]

		self.AboutText += _("FLASH") + '\n\n'
		self.AboutText += _("Total:") + "\t" + RamTotal + "\n"
		self.AboutText += _("Free:") + "\t" + RamFree + "\n\n"

		self["AboutScrollLabel"].setText(self.AboutText)
		self["actions"].setEnabled(True)

class TranslationInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Translation"))
		# don't remove the string out of the _(), or it can't be "translated" anymore.

		# TRANSLATORS: Add here whatever should be shown in the "translator" about screen, up to 6 lines (use \n for newline)
		info = _("TRANSLATOR_INFO")

		if info == "TRANSLATOR_INFO":
			info = "(N/A)"

		infolines = _("").split("\n")
		infomap = {}
		for x in infolines:
			l = x.split(': ')
			if len(l) != 2:
				continue
			(type, value) = l
			infomap[type] = value
		print(infomap)

		self["key_red"] = Button(_("Cancel"))
		self["TranslationInfo"] = StaticText(info)
		self["lab1"] = StaticText(_("OpenVision"))
		self["lab2"] = StaticText(_("Lets define enigma2 once more"))
		self["lab3"] = StaticText(_("Report problems to:"))
		self["lab4"] = StaticText(_("https://openvision.tech"))
		self["lab5"] = StaticText(_("Sources are available at:"))
		self["lab6"] = StaticText(_("https://github.com/OpenVisionE2"))

		translator_name = infomap.get("Language-Team", "none")
		if translator_name == "none":
			translator_name = infomap.get("Last-Translator", "")

		self["TranslatorName"] = StaticText(translator_name)

		self["actions"] = ActionMap(["SetupActions"],
			{
				"cancel": self.close,
				"ok": self.close,
			})

class CommitInfoDevelop(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.skinName = "CommitInfoDevelop"
        self.setup_title = _("Novedades Alvaro")
        self.setTitle(self.setup_title)
        self["news"] = ScrollLabel()

        self["Actions"] = ActionMap(['OkCancelActions', 'ShortcutActions',"ColorActions","DirectionActions"],
            {
            "cancel" : self.cerrar,
            "ok" : self.cerrar,
            "up": self["news"].pageUp,
            "down": self["news"].pageDown,
            "left": self["news"].pageUp,
            "right": self["news"].pageDown,
            })
        self['news'].setText(news(URL))

	self["lab1"] = StaticText(_("OpenVision"))
	self["lab2"] = StaticText(_("Lets define enigma2 once more"))
	self["lab3"] = StaticText(_("Report problems to:"))
	self["lab4"] = StaticText(_("https://openvision.tech"))
	self["lab5"] = StaticText(_("Sources are available at:"))
	self["lab6"] = StaticText(_("https://github.com/OpenVisionE2"))

    def cerrar(self):
        self.close()

	def readGithubCommitLogs(self):
		url = self.projects[self.project][0]
		commitlog = ""
		from datetime import datetime
		from json import loads
		from urllib2 import urlopen
		try:
			commitlog += 80 * '-' + '\n'
			commitlog += url.split('/')[-2] + '\n'
			commitlog += 80 * '-' + '\n'
			try:
				# OpenPli 5.0 uses python 2.7.11 and here we need to bypass the certificate check
				from ssl import _create_unverified_context
				if PY2:
					log = loads(urllib2.urlopen(url, timeout=5, context=_create_unverified_context()).read())
				else:
					log = loads(urllib.request.urlopen(url, timeout=5, context=_create_unverified_context()).read())
			except:
				if PY2:
					log = loads(urllib2.urlopen(url, timeout=5).read())
				else:
					log = loads(urllib.request.urlopen(url, timeout=5).read())
			for c in log:
				creator = c['commit']['author']['name']
				title = c['commit']['message']
				date = datetime.strptime(c['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%x %X')
				commitlog += date + ' ' + creator + '\n' + title + 2 * '\n'
			commitlog = commitlog.encode('utf-8')
			self.cachedProjects[self.projects[self.project][1]] = commitlog
		except:
			commitlog += _("Currently the commit log cannot be retrieved - please try later again")
		self["AboutScrollLabel"].setText(commitlog)

	def updateCommitLogs(self):
		if self.projects[self.project][1] in self.cachedProjects:
			self["AboutScrollLabel"].setText(self.cachedProjects[self.projects[self.project][1]])
		else:
			self["AboutScrollLabel"].setText(_("Please wait"))
			self.Timer.start(50, True)

	def left(self):
		self.project = self.project == 0 and len(self.projects) - 1 or self.project - 1
		self.updateCommitLogs()

	def right(self):
		self.project = self.project != len(self.projects) - 1 and self.project + 1 or 0
		self.updateCommitLogs()

class MemoryInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.close,
				"ok": self.getMemoryInfo,
				"green": self.getMemoryInfo,
				"blue": self.clearMemory,
			})

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Refresh"))
		self["key_blue"] = Label(_("Clear"))

		self['lmemtext'] = Label()
		self['lmemvalue'] = Label()
		self['rmemtext'] = Label()
		self['rmemvalue'] = Label()

		self['pfree'] = Label()
		self['pused'] = Label()
		self["slide"] = ProgressBar()
		self["slide"].setValue(100)

		self["lab1"] = StaticText(_("OpenVision"))
		self["lab2"] = StaticText(_("Lets define enigma2 once more"))
		self["lab3"] = StaticText(_("Report problems to:"))
		self["lab4"] = StaticText(_("https://openvision.tech"))
		self["lab5"] = StaticText(_("Sources are available at:"))
		self["lab6"] = StaticText(_("https://github.com/OpenVisionE2"))

		self["params"] = MemoryInfoSkinParams()

		self['info'] = Label(_("This info is for developers only.\nFor normal users it is not relevant.\nPlease don't panic if you see values displayed looking suspicious!"))

		self.setTitle(_("Memory Info"))
		self.onLayoutFinish.append(self.getMemoryInfo)

	def getMemoryInfo(self):
		try:
			ltext = rtext = ""
			lvalue = rvalue = ""
			mem = 1
			free = 0
			rows_in_column = self["params"].rows_in_column
			for i, line in enumerate(open('/proc/meminfo','r')):
				s = line.strip().split(None, 2)
				if len(s) == 3:
					name, size, units = s
				elif len(s) == 2:
					name, size = s
					units = ""
				else:
					continue
				if name.startswith("MemTotal"):
					mem = int(size)
				if name.startswith("MemFree") or name.startswith("Buffers") or name.startswith("Cached"):
					free += int(size)
				if i < rows_in_column:
					ltext += "".join((name,"\n"))
					lvalue += "".join((size," ",units,"\n"))
				else:
					rtext += "".join((name,"\n"))
					rvalue += "".join((size," ",units,"\n"))
			self['lmemtext'].setText(ltext)
			self['lmemvalue'].setText(lvalue)
			self['rmemtext'].setText(rtext)
			self['rmemvalue'].setText(rvalue)
			self["slide"].setValue(int(100.0*(mem-free)/mem+0.25))
			self['pfree'].setText("%.1f %s" % (100.*free/mem,'%'))
			self['pused'].setText("%.1f %s" % (100.*(mem-free)/mem,'%'))
		except Exception, e:
			print("[About] getMemoryInfo FAIL:", e)

	def clearMemory(self):
		eConsoleAppContainer().execute("sync")
		open("/proc/sys/vm/drop_caches", "w").write("3")
		self.getMemoryInfo()

class MemoryInfoSkinParams(GUIComponent):
	def __init__(self):
		GUIComponent.__init__(self)
		self.rows_in_column = 25

	def applySkin(self, desktop, screen):
		if self.skinAttributes is not None:
			attribs = [ ]
			for (attrib, value) in self.skinAttributes:
				if attrib == "rowsincolumn":
					self.rows_in_column = int(value)
			self.skinAttributes = attribs
			applySkin = GUIComponent
		return applySkin()

	GUI_WIDGET = eLabel

class Troubleshoot(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Troubleshoot"))
		self["AboutScrollLabel"] = ScrollLabel(_("Please wait"))
		self["key_red"] = Button()
		self["key_green"] = Button()
		self["lab1"] = StaticText(_("OpenVision"))
		self["lab2"] = StaticText(_("Lets define enigma2 once more"))
		self["lab3"] = StaticText(_("Report problems to:"))
		self["lab4"] = StaticText(_("https://openvision.tech"))
		self["lab5"] = StaticText(_("Sources are available at:"))
		self["lab6"] = StaticText(_("https://github.com/OpenVisionE2"))

		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions"],
			{
				"cancel": self.close,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown,
				"moveUp": self["AboutScrollLabel"].homePage,
				"moveDown": self["AboutScrollLabel"].endPage,
				"left": self.left,
				"right": self.right,
				"red": self.red,
				"green": self.green,
			})

		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.appClosed)
		self.container.dataAvail.append(self.dataAvail)
		self.commandIndex = 0
		self.updateOptions()
		self.onLayoutFinish.append(self.run_console)

	def left(self):
		self.commandIndex = (self.commandIndex - 1) % len(self.commands)
		self.updateKeys()
		self.run_console()

	def right(self):
		self.commandIndex = (self.commandIndex + 1) % len(self.commands)
		self.updateKeys()
		self.run_console()

	def red(self):
		if self.commandIndex >= self.numberOfCommands:
			self.session.openWithCallback(self.removeAllLogfiles, MessageBox, _("Do you want to remove all the crash logfiles"), default=False)
		else:
			self.close()

	def green(self):
		if self.commandIndex >= self.numberOfCommands:
			try:
				os.remove(self.commands[self.commandIndex][4:])
			except:
				pass
			self.updateOptions()
		self.run_console()

	def removeAllLogfiles(self, answer):
		if answer:
			for fileName in self.getLogFilesList():
				try:
					os.remove(fileName)
				except:
					pass
			self.updateOptions()
			self.run_console()

	def appClosed(self, retval):
		if retval:
			self["AboutScrollLabel"].setText(_("An error occurred - Please try again later"))

	def dataAvail(self, data):
		self["AboutScrollLabel"].appendText(data)

	def run_console(self):
		self["AboutScrollLabel"].setText("")
		self.setTitle("%s - %s" % (_("Troubleshoot"), self.titles[self.commandIndex]))
		command = self.commands[self.commandIndex]
		if command.startswith("cat "):
			try:
				self["AboutScrollLabel"].setText(open(command[4:], "r").read())
			except:
				self["AboutScrollLabel"].setText(_("Logfile does not exist anymore"))
		else:
			try:
				if self.container.execute(command):
					raise Exception, "failed to execute: ", command
			except Exception, e:
				self["AboutScrollLabel"].setText("%s\n%s" % (_("An error occurred - Please try again later"), e))

	def cancel(self):
		self.container.appClosed.remove(self.appClosed)
		self.container.dataAvail.remove(self.dataAvail)
		self.container = None
		self.close()

	def getDebugFilesList(self):
		import glob
		return [x for x in sorted(glob.glob("/home/root/logs/enigma2_debug_*.log"), key=lambda x: os.path.isfile(x) and os.path.getmtime(x))]

	def getLogFilesList(self):
		import glob
		home_root = "/home/root/logs/enigma2_crash.log"
		tmp = "/tmp/enigma2_crash.log"
		return [x for x in sorted(glob.glob("/mnt/hdd/*.log"), key=lambda x: os.path.isfile(x) and os.path.getmtime(x))] + (os.path.isfile(home_root) and [home_root] or []) + (os.path.isfile(tmp) and [tmp] or [])

	def updateOptions(self):
		self.titles = ["dmesg", "ifconfig", "df", "top", "ps", "messages"]
		self.commands = ["dmesg", "ifconfig", "df -h", "top -n 1", "ps -l", "cat /var/volatile/log/messages"]
		install_log = "/home/root/autoinstall.log"
		if os.path.isfile(install_log):
				self.titles.append("%s" % install_log)
				self.commands.append("cat %s" % install_log)
		self.numberOfCommands = len(self.commands)
		fileNames = self.getLogFilesList()
		if fileNames:
			totalNumberOfLogfiles = len(fileNames)
			logfileCounter = 1
			for fileName in reversed(fileNames):
				self.titles.append("logfile %s (%s/%s)" % (fileName, logfileCounter, totalNumberOfLogfiles))
				self.commands.append("cat %s" % (fileName))
				logfileCounter += 1
		fileNames = self.getDebugFilesList()
		if fileNames:
			totalNumberOfLogfiles = len(fileNames)
			logfileCounter = 1
			for fileName in reversed(fileNames):
				self.titles.append("debug log %s (%s/%s)" % (fileName, logfileCounter, totalNumberOfLogfiles))
				self.commands.append("tail -n 2500 %s" % (fileName))
				logfileCounter += 1
		self.commandIndex = min(len(self.commands) - 1, self.commandIndex)
		self.updateKeys()

	def updateKeys(self):
		self["key_red"].setText(_("Cancel") if self.commandIndex < self.numberOfCommands else _("Remove all logfiles"))
		self["key_green"].setText(_("Refresh") if self.commandIndex < self.numberOfCommands else _("Remove this logfile"))
