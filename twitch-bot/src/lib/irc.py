import socket, re, time, sys
from functions_general import *
import cron
import thread

class irc:
	
	def __init__(self, config):
		self.config = config

        def bootstrap_channels(self):
		startup_channels = []
                entering_channels = []
                leaving_channels = []
		f = open('/home/ubuntu/top500.txt')
		for line in f:
			startup_channels.append('#' + line.rstrip())

                for lchan in self.config['channels']:
                        if lchan not in startup_channels:
                                leaving_channels.append(lchan)
                                self.config['channels'].remove(lchan)

		for schan in startup_channels:
                        if schan not in self.config['channels']:
                                entering_channels.append(schan)
                                self.config['channels'].append(schan)

                self.leave_all_channels(leaving_channels)
                self.join_all_channels(entering_channels)

	def check_for_message(self, data):
		if re.match(r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$', data):
			return True

	def check_is_command(self, message, valid_commands):
		for command in valid_commands:
			if command == message:
				return True

	def check_for_connected(self, data):
		if re.match(r'^:.+ 001 .+ :connected to TMI$', data):
			return True

	def check_for_ping(self, data):
		if data[:4] == "PING": 
			self.sock.send('PONG')

	def get_message(self, data):
		return {
			'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
			'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
			'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0].decode('utf8')
		}

	def check_login_status(self, data):
		if re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data):
			return False
		else:
			return True

	def send_message(self, channel, message):
		self.sock.send('PRIVMSG %s :%s\n' % (channel, message.encode('utf-8')))

	def get_irc_socket_object(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(10)

		self.sock = sock

		try:
			sock.connect((self.config['server'], self.config['port']))
		except:
			pp('Cannot connect to server (%s:%s).' % (self.config['server'], self.config['port']), 'error')
			sys.exit()

		sock.settimeout(None)

		sock.send('USER %s\r\n' % self.config['username'])
		sock.send('PASS %s\r\n' % self.config['oauth_password'])
		sock.send('NICK %s\r\n' % self.config['username'])

		if self.check_login_status(sock.recv(1024)):
			pp('Login successful.')
		else:
			pp('Login unsuccessful. (hint: make sure your oauth token is set in self.config/self.config.py).', 'error')
			sys.exit()

		# start threads for channels that have cron messages to run
		for channel in self.config['channels']:
			if channel in self.config['cron']:
				if self.config['cron'][channel]['run_cron']:
					thread.start_new_thread(cron.cron(self, channel).run, ())

		self.join_channels(self.channels_to_string(self.config['channels']))


		return sock

	def channels_to_string(self, channel_list):
		return ','.join(channel_list)

	def join_channels(self, channels):
		pp('Joining channels %s.' % channels)
		self.sock.send('JOIN %s\r\n' % channels)
		pp('Joined channels.')
                time.sleep(0.07)

        def join_all_channels(self, channels):
                for channel in channels:
                        pp('Joining channels %s.' % channel)
                        self.sock.send('JOIN %s\r\n' %channel)
                        pp('Joined channels.')
                        time.sleep(0.09)

	def leave_channels(self, channels):
		pp('Leaving chanels %s,' % channels)
		self.sock.send('PART %s\r\n' % channels)
		pp('Left channels.')
                time.sleep(0.07)

        def leave_all_channels(self, channels):
                for channel in channels:
                        pp('Leaving channels %s.' % channel)
                        self.sock.send('PART %s\r\n' %channel)
                        pp('Left channels.')
                        time.sleep(0.09)
