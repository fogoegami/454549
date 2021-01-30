from Tools.Directories import SCOPE_SKIN, resolveFilename

hw_info = None

class HardwareInfo:
	device_name = _("unavailable")
	device_brandname = None
	device_model = None
	device_brand = _("No Disponible")
	device_version = ""
	device_revision = ""
	device_hdmi = False

	def __init__(self):
		global hw_info
		if hw_info:
			return
		hw_info = self

		print("[HardwareInfo] Scanning hardware info")
		# Version
		try:
			self.device_version = open("/proc/stb/info/version").read().strip()
		except:
			pass

		# Revision
		try:
			self.device_revision = open("/proc/stb/info/board_revision").read().strip()
		except:
			pass

		# Name ... bit odd, but history prevails
		try:
			self.device_name = open("/proc/stb/info/model").read().strip()
		except:
			pass

		# Brandname ... bit odd, but history prevails
		try:
			self.device_brandname = open("/proc/stb/info/brandname").read().strip()
		except:
			pass

		# Model
		for line in open((resolveFilename(SCOPE_SKIN, 'hw_info/hw_info.cfg')), 'r'):
			if not line.startswith('#') and not line.isspace():
				l = line.strip().replace('\t', ' ')
				if ' ' in l:
					infoFname, prefix = l.split()
				else:
					infoFname = l
					prefix = ""
				try:
					self.device_model = prefix + open("/proc/stb/info/" + infoFname).read().strip()
					break
				except:
					pass

		if self.device_model.endswith(("9000de")):
			self.device_brand = "Golden Interstar"
		elif self.device_model.startswith(("hd")):
			self.device_brand = "Mut@nt"
		elif self.device_model.startswith(("vs")):
			self.device_brand = "Mut@nt"
		elif self.device_model.startswith(("vu")):
			self.device_brand = "Vuplus"
		elif self.device_model.startswith(("ini-8000")):
			self.device_brand = "Atemio"
		elif self.device_model.startswith(("os")):
			self.device_brand = "Edision"
		elif self.device_model.startswith(("gb")):
			self.device_brand = "GigaBlue"

			self.device_model = self.device_model or self.device_name
			self.device_hw = self.device_model
			self.machine_name = self.device_model

		if self.device_model.startswith(("et9", "et4", "et5", "et6", "et7")):
			self.machine_name = "%sx00" % self.device_model[:3]
		elif self.device_model == "et11000":
			self.machine_name = "et1x000"
		elif self.device_brandname == "Zgemma":
			self.device_model = self.device_name
			self.machine_name = self.device_name
		else:
			self.machine_name = self.device_model

		if self.device_revision:
			self.device_string = "%s (%s-%s)" % (self.device_model, self.device_revision, self.device_version)
		elif self.device_version:
			self.device_string = "%s (%s)" % (self.device_model, self.device_version)
		else:
			self.device_string = self.device_hw

		# only some early DMM boxes do not have HDMI hardware
		self.device_hdmi =	self.device_model not in ("dm800","dm8000")

		print("[HardwareInfo] Detected: " + self.get_device_string())

	def get_device_name(self):
		return hw_info.device_name

	def get_device_model(self):
		return hw_info.device_model

	def get_device_brand(self):
		return hw_info.device_brand

	def get_device_version(self):
		return hw_info.device_version

	def get_device_revision(self):
		return hw_info.device_revision

	def get_device_string(self):
		if hw_info.device_revision:
			return "%s (%s-%s)" % (hw_info.device_model, hw_info.device_revision, hw_info.device_version)
		elif hw_info.device_version:
			return "%s (%s)" % (hw_info.device_model, hw_info.device_version)
		return hw_info.device_model

	def get_machine_name(self):
		return hw_info.machine_name

	def has_hdmi(self):
		return hw_info.device_hdmi
