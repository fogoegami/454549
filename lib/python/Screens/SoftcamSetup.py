from enigma import eTimer, getDesktop
from os.path import isfile

from Screens.MessageBox import MessageBox
from Components.ActionMap import HelpableActionMap
from Components.config import ConfigSelection, NoSave, config
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText
from Screens.Setup import Setup
from Tools.camcontrol import CamControl
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists, fileHas
from Tools.GetEcmInfo import GetEcmInfo

class SoftcamSetup(Setup):
	def __init__(self, session):
		self.softcam = CamControl("softcam")
		self.cardserver = CamControl("cardserver")
		self.ecminfo = GetEcmInfo()
		restartOptions = [
			("", _("Don't restart")),
			("s", _("Restart softcam"))
		]
		config.misc.softcams = NoSave(ConfigSelection(choices=self.softcam.getList()))
		config.misc.softcams.value = self.softcam.current()
		cardservers = self.cardserver.getList()
		if cardservers:
			default = self.cardserver.current()
			restartOptions.extend([("c", _("Restart cardserver")), ("sc", _("Restart both"))])
		else:
			cardservers = [("", _("None"))]
			default = ""
		config.misc.cardservers = NoSave(ConfigSelection(choices=cardservers))
		config.misc.cardservers.value = default
		config.misc.restarts = NoSave(ConfigSelection(default="", choices=restartOptions))
		Setup.__init__(self, session=session, setup="softcamsettings")
		self["key_yellow"] = StaticText()
		self["key_blue"] = StaticText()
		self["restartActions"] = HelpableActionMap(self, ["ColorActions"], {
			"yellow": (self.restart, _("Immediately restart selected devices."))
		}, prio=0, description=_("Softcam Actions"))
		self["restartActions"].setEnabled(False)
		self["infoActions"] = HelpableActionMap(self, ["ColorActions"], {
			"blue": (self.softcamInfo, _("Display oscam information."))
		}, prio=0, description=_("Softcam Actions"))
		self["infoActions"].setEnabled(False)
		(newEcmFound, ecmInfo) = self.ecminfo.getEcm()
		self["info"] = ScrollLabel("".join(ecmInfo))
		self.EcmInfoPollTimer = eTimer()
		self.EcmInfoPollTimer.callback.append(self.setEcmInfo)
		self.EcmInfoPollTimer.start(1000)
		self.onShown.append(self.updateButtons)

	def selectionChanged(self):
		self.updateButtons()
		Setup.selectionChanged(self)

	def changedEntry(self):
		self.updateButtons()
		Setup.changedEntry(self)

	def keySave(self):
		device = ""
		if hasattr(self, "cardservers") and (config.misc.cardservers.value != self.cardserver.current()):
			device = "sc"
		elif config.misc.softcams.value != self.softcam.current():
			device = "s"
		if device:
			self.restart(device="e%s" % device)
		else:
			Setup.keySave(self)

	def keyCancel(self):
		config.misc.softcams.value = config.misc.softcams.default
		config.misc.cardservers.value = config.misc.cardservers.default
		config.misc.restarts.value = config.misc.restarts.default
		Setup.keyCancel(self)

	def updateButtons(self):
		if config.misc.restarts.value:
			self["key_yellow"].setText(_("Restart"))
			self["restartActions"].setEnabled(True)
		else:
			self["key_yellow"].setText("")
			self["restartActions"].setEnabled(False)
		if self["config"].getCurrent()[1] == config.misc.softcams and config.misc.softcams.value and config.misc.softcams.value.lower() != "none":
			self["key_blue"].setText(_("Info"))
			self["infoActions"].setEnabled(True)
		else:
			self["key_blue"].setText("")
			self["infoActions"].setEnabled(False)

	def softcamInfo(self):
		ppanelFilename = "/etc/ppanels/%s.xml" % config.misc.softcams.value
		if "oscam" in config.misc.softcams.value.lower():
			from Screens.OScamInfo import OscamInfoMenu
			self.session.open(OscamInfoMenu)
		elif "ncam" in config.misc.softcams.value.lower():
			from Screens.NcamInfo import NcamInfoMenu
			self.session.open(NcamInfoMenu)
		elif "cccam" in config.misc.softcams.value.lower():
			from Screens.CCcamInfo import CCcamInfoMain
			self.session.open(CCcamInfoMain)
		elif "cccam" in config.misc.softcams.value.lower() and isfile(resolveFilename(SCOPE_PLUGINS, "Extensions/CCcamInfo/plugin.pyo")) or isfile(resolveFilename(SCOPE_PLUGINS, "Extensions/CCcamInfo/plugin.py")):
			from Plugins.Extensions.CCcamInfo.plugin import CCcamInfoMain
			self.session.open(CCcamInfoMain)
		elif isfile(ppanelFilename) and isfile(resolveFilename(SCOPE_PLUGINS, "Extensions/PPanel/plugin.pyo")) or isfile(resolveFilename(SCOPE_PLUGINS, "Extensions/PPanel/plugin.py")):
			from Plugins.Extensions.PPanel.ppanel import PPanel
			self.session.open(PPanel, name="%s PPanel" % config.misc.softcams.value, node=None, filename=ppanelFilename, deletenode=None)

	def restart(self, device=None):
		self.device = config.misc.restarts.value if device is None else device
		msg = []
		if "s" in self.device:
			msg.append(_("softcam"))
		if "c" in self.device:
			msg.append(_("cardserver"))
		msg = (" %s " % _("and")).join(msg)
		self.mbox = self.session.open(MessageBox, _("Please wait, restarting %s.") % msg, MessageBox.TYPE_INFO)
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.doStop)
		self.activityTimer.start(100, False)

	def doStop(self):
		self.activityTimer.stop()
		if "s" in self.device:
			self.softcam.command("stop")
		if "c" in self.device:
			self.cardserver.command("stop")
		self.oldref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		self.session.nav.stopService()
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.doStart)
		self.activityTimer.start(1000, False)

	def doStart(self):
		self.activityTimer.stop()
		del self.activityTimer
		if "s" in self.device:
			self.softcam.select(config.misc.softcams.value)
			self.softcam.command("start")
		if "c" in self.device:
			self.cardserver.select(config.misc.cardservers.value)
			self.cardserver.command("start")
		if self.mbox:
			self.mbox.close()
		self.session.nav.playService(self.oldref, adjust=False)
		if "e" in self.device:
			Setup.keySave(self)

	def setEcmInfo(self):
		(newEcmFound, ecmInfo) = self.ecminfo.getEcm()
		if newEcmFound:
			self["info"].setText("".join(ecmInfo))

	def restartSoftcam(self):
		self.restart(device="s")

	def restartCardServer(self):
		if hasattr(self, "cardservers"):
			self.restart(device="c")