import ctypes, time, os, sys, smtplib, subprocess
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from mss import MSSWindows as mss_class # https://pypi.python.org/pypi/mss/0.0.7

# Credit for ctype stuff to: http://stackoverflow.com/a/13615802
SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions 
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

class Screenshmailer():
	def __init__(self):		
		os.remove('monitor-1.png')
		self.take_screenshot()
		self.send_email()
			
	def take_screenshot(self):
		# Try and take a screenshot.
		mss = mss_class()
		try:
			# Screenshot of the monitor 1
			for filename in mss.save(output='monitor-%d.png', screen=1):
				print('File: "{}" created.'.format(filename))
		except ScreenshotError as ex:
			print(ex)
	
	def send_email(self):
		# Get the recipients.  Expects that the second argument
		# is the '-r' (recipients) argument and is in this format:
		#	-r:email@address.com,email2@address.com
		args = sys.argv
		toaddrs = []
		toaddrs.append(args[1].split(":")[1])
		
		FROM_EMAIL_ADDR = 'email@gmail.com'
		FROM_EMAIL_PWD = 'emailPassword'
		
		# Create the root message and fill in the from, to, and subject
		msg = MIMEMultipart()
		msg['Subject'] = 'DEVSERVER screenshot'
		msg['From'] = FROM_EMAIL_ADDR
		msg['To'] = ','.join(toaddrs)
		msg.preamble = 'This is a multi-part message in MIME format.'
		
		cur_time = datetime.now()
		msgText = MIMEText("Datetime.now: <b><i>" + str(cur_time) + "</i></b><br><br><img src=\"cid:scrnsht\">", 'html')
		msg.attach(msgText)
		
		# Attach image
		fp = open('monitor-1.png', 'rb')
		msgImage = MIMEImage(fp.read())
		fp.close()
		
		msgImage.add_header('Content-ID', '<scrnsht>')
		msg.attach(msgImage)
		
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(FROM_EMAIL_ADDR, FROM_EMAIL_PWD)
		server.send_message(msg)
		server.quit()
		
		print ("Email sent at: ", cur_time)

# Actual Functions

def PressKeyDown(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( hexKeyCode, 0x48, 0, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( hexKeyCode, 0x48, 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def PressKey(hexKeyCode):
	PressKeyDown(hexKeyCode)
	ReleaseKey(hexKeyCode)
	
def Connect():
	os.system('mstsc /f')
	time.sleep(2)
	# Tab to 'Connect'
	PressKey(0x09)
	PressKey(0x09)
	# Hit Enter to type in login info
	PressKey(0x0D)
	time.sleep(2) 
	# Enter in login info one key at a time
		
def TakeScreenshot():
	ss = Screenshmailer()
	
def get_pid(proc_name):
	# Returns -1 if PID not found or the PID.
	retval = ''
	cmd = 'cmd.exe /C tasklist | find "mstsc"'
	out = b''
	try:
		out = subprocess.check_output(cmd)
	except subprocess.CalledProcessError:
		retval = '-1'
	else:
		strout = out.decode(encoding='UTF-8')
		proc = strout.split()
		retval = proc[1]		
	return retval

def Disconnect():
	proc = 'mstsc.exe'
	pid = get_pid(proc)
	
	if '-1' not in pid:
		os.system('taskkill /f /im ' + proc)
	else:
		print (proc, ' not found in tasklist')
	
	
if __name__ =="__main__":
	TakeScreenshot()
	Disconnect()
	