from __future__ import print_function
import threading
lock = threading.Lock()

notifications = [ ]
notificationAdded = [ ]

# notifications which are currently on screen (and might be closed by similiar notifications)
current_notifications = [ ]

def __AddNotification(fnc, screen, id, *args, **kwargs):
	if ".MessageBox'>" in str(screen):
		kwargs["simple"] = True
	if ".Standby'>" in str(screen):
		removeCIdialog()
	lock.acquire(True)
	notifications.append((fnc, screen, args, kwargs, id))
	lock.release()
	for x in notificationAdded:
		x()

def AddNotification(screen, *args, **kwargs):
	AddNotificationWithCallback(None, screen, *args, **kwargs)

def AddNotificationWithCallback(fnc, screen, *args, **kwargs):
	__AddNotification(fnc, screen, None, *args, **kwargs)

def AddNotificationParentalControl(fnc, screen, *args, **kwargs):
	RemovePopup("Parental control")
	__AddNotification(fnc, screen, "Parental control", *args, **kwargs)

def AddNotificationWithID(id, screen, *args, **kwargs):
	__AddNotification(None, screen, id, *args, **kwargs)

def AddNotificationWithIDCallback(fnc, id, screen, *args, **kwargs):
	__AddNotification(fnc, screen, id, *args, **kwargs)

# Entry to only have one pending item with an id.
# Only use this if you don't mind losing the callback for skipped calls.
#
def AddNotificationWithUniqueIDCallback(fnc, id, screen, *args, **kwargs):
	for x in notifications:
		if x[4] and x[4] == id:    # Already there...
			return
	__AddNotification(fnc, screen, id, *args, **kwargs)

# we don't support notifications with callback and ID as this
# would require manually calling the callback on cancelled popups.

def RemovePopup(id):
	# remove similiar notifications
	print("[Notifications] RemovePopup, id =", id)
	for x in notifications:
		if x[4] and x[4] == id:
			print("[Notifications] found in notifications")
			lock.acquire(True)
			notifications.remove(x)
			lock.release()

	for x in current_notifications:
		if x[0] == id:
			print("[Notifications] found in current notifications")
			x[1].close()

from Screens.MessageBox import MessageBox

def AddPopup(text, type, timeout, id = None):
	if id is not None:
		RemovePopup(id)
	print("[Notifications] AddPopup, id =", id)
	AddNotificationWithID(id, MessageBox, text = text, type = type, timeout = timeout, close_on_any_key = True)

def AddPopupWithCallback(fnc, text, type, timeout, id = None):
	if id is not None:
		RemovePopup(id)
	print("[Notifications] AddPopup, id =", id)
	AddNotificationWithIDCallback(fnc, id, MessageBox, text = text, type = type, timeout = timeout, close_on_any_key = False)

def removeCIdialog():
	import NavigationInstance
	if NavigationInstance.instance and NavigationInstance.instance.wasTimerWakeup():
		import Screens.Ci
		for slot in Screens.Ci.CiHandler.dlgs:
			if hasattr(Screens.Ci.CiHandler.dlgs[slot], "forceExit"):
				Screens.Ci.CiHandler.dlgs[slot].tag = "WAIT"
				Screens.Ci.CiHandler.dlgs[slot].forceExit()
