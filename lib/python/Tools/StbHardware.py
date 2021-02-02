#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from os import path
from fcntl import ioctl
from struct import pack, unpack
from time import time, localtime, gmtime
from enigma import getBoxType
from Components.SystemInfo import SystemInfo
from Tools.Directories import fileExists

def getBoxProc():
	procmodel = "unknown"
	try:
		if fileExists("/proc/stb/info/hwmodel"):
			procmodel = open("/proc/stb/info/hwmodel", "r").readline().strip().lower()
		elif fileExists("/proc/stb/info/azmodel"):
			procmodel = open("/proc/stb/info/azmodel", "r").readline().strip().lower()
		elif fileExists("/proc/stb/info/gbmodel"):
			procmodel = open("/proc/stb/info/gbmodel", "r").readline().strip().lower()
		elif fileExists("/proc/stb/info/vumodel") and not fileExists("/proc/stb/info/boxtype"):
			procmodel = open("/proc/stb/info/vumodel", "r").readline().strip().lower()
		elif fileExists("/proc/stb/info/boxtype") and not fileExists("/proc/stb/info/model"):
			procmodel = open("/proc/stb/info/boxtype", "r").readline().strip().lower()
		elif fileExists("/proc/boxtype"):
			procmodel = open("/proc/boxtype", "r").readline().strip().lower()
		elif fileExists("/etc/modules-load.d/_xpeedlx3.conf"):
			procmodel = "Xpeed-LX3"
		elif fileExists("/etc/modules-load.d/_osmio4kplus.conf"):
			procmodel = "OS mio+ 4K"
		elif fileExists("/etc/modules-load.d/_gbtrio4k.conf"):
			procmodel = "GB TRIO 4K"
		elif fileExists("/etc/modules-load.d/_gbip4k.conf"):
			procmodel = "GB IP 4K"
		elif fileExists("/etc/modules-load.d/_sf8008.conf"):
			procmodel = "SF 8008 UHD"
		elif fileExists("/etc/modules-load.d/_sf8008m.conf"):
			procmodel = "SF 8008 MINI UHD"
		else:
			procmodel = open("/proc/stb/info/model", "r").readline().strip().lower()
	except IOError:
		print("[StbHardware] getBoxProc failed!")
	return procmodel

def getFPVersion():
	ret = None
	try:
		ret = int(open("/proc/stb/fp/version", "r").read())
	except IOError:
		try:
			fp = open("/dev/dbox/fp0")
			ret = ioctl(fp.fileno(),0)
		except IOError:
			try:
				ret = open("/sys/firmware/devicetree/base/bolt/tag", "r").read().rstrip("\0")
			except:
				print("getFPVersion failed!")
	return ret

def setFPWakeuptime(wutime):
	try:
		open("/proc/stb/fp/wakeup_time", "w").write(str(wutime))
	except IOError:
		try:
			fp = open("/dev/dbox/fp0")
			ioctl(fp.fileno(), 6, pack('L', wutime)) # set wake up
			fp.close()
		except IOError:
			print("[StbHardware] setFPWakeupTime failed!")

def setRTCoffset(forsleep=None):
	import time
	if time.localtime().tm_isdst == 0:
		forsleep = 7200+time.timezone
	else:
		forsleep = 3600-time.timezone

	t_local = time.localtime(int(time.time()))

	# Set RTC OFFSET (diff. between UTC and Local Time)
	try:
		open("/proc/stb/fp/rtc_offset", "w").write(str(forsleep))
		print("[StbHardware] set RTC offset to %s sec." % (forsleep))
	except IOError:
		print("[StbHardware] setRTCoffset failed!")

def setRTCtime(wutime):
	if path.exists("/proc/stb/fp/rtc_offset"):
		setRTCoffset()
	try:
		open("/proc/stb/fp/rtc", "w").write(str(wutime))
	except IOError:
		try:
			fp = open("/dev/dbox/fp0")
			ioctl(fp.fileno(), 0x101, pack('L', wutime)) # set wake up
			fp.close()
		except IOError:
			print("[StbHardware] setRTCtime failed!")

def getFPWakeuptime():
	ret = 0
	try:
		ret = int(open("/proc/stb/fp/wakeup_time", "r").read())
	except IOError:
		try:
			fp = open("/dev/dbox/fp0")
			ret = unpack('L', ioctl(fp.fileno(), 5, '	 '))[0] # get wakeuptime
			fp.close()
		except IOError:
			print("[StbHardware] getFPWakeupTime failed!")
	return ret

wasTimerWakeup = None

def getFPWasTimerWakeup(check = False):
	global wasTimerWakeup
	isError = False
	if wasTimerWakeup is not None:
		if check:
			return wasTimerWakeup, isError
		return wasTimerWakeup
	wasTimerWakeup = False
	try:
		wasTimerWakeup = int(open("/proc/stb/fp/was_timer_wakeup", "r").read()) and True or False
		open("/tmp/was_timer_wakeup.txt", "w").write(str(wasTimerWakeup))
	except:
		try:
			fp = open("/dev/dbox/fp0")
			wasTimerWakeup = unpack('B', ioctl(fp.fileno(), 9, ' '))[0] and True or False
			fp.close()
		except IOError:
			print("[StbHardware] wasTimerWakeup failed!")
			isError = True
	if wasTimerWakeup:
		# clear hardware status
		clearFPWasTimerWakeup()
	if check:
		return wasTimerWakeup, isError
	return wasTimerWakeup

def clearFPWasTimerWakeup():
	try:
		open("/proc/stb/fp/was_timer_wakeup", "w").write('0')
	except:
		try:
			fp = open("/dev/dbox/fp0")
			ioctl(fp.fileno(), 10)
			fp.close()
		except IOError:
			print("clearFPWasTimerWakeup failed!")
