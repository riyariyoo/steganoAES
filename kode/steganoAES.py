from PIL import Image 
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import binascii
import optparse


def rgb2hex(r, g, b):
	return '#{:02x}{:02x}{:02x}'.format(r, g, b) 

def hex2rgb(hexcode):	
	return tuple(map(ord, hexcode[1:].decode('hex')))

def str2bin(message):	
	binary = bin(int(binascii.hexlify(message), 16))
	return binary[2:]

def bin2str(binary):
	message = binascii.unhexlify('%x' % (int('0b'+binary,2)))
	return message

def encodeLSB(hexcode, digit):
	if hexcode[-1] in ('0','1', '2', '3', '4', '5'):
		hexcode = hexcode[:-1] + digit 
		return hexcode
	else:
		return None

def decodeLSB(hexcode):
	if hexcode[-1] in ('0', '1'):
		return hexcode[-1]
	else:
		return None

def encodeAES(plain,key):
	IV = 16 * '\x00'   
	mode = AES.MODE_CBC
	encryptor = AES.new(key, mode, IV)
	#plain = plain 
	ciphertext = encryptor.encrypt(plain)

	return ciphertext

def decodeAES(ciphertext,key):
	IV = 16 * '\x00'
	mode = AES.MODE_CBC
	decryptor = AES.new(key, mode, IV)
	plain = decryptor.decrypt(ciphertext)
	
	return plain

######################################	

def hide(filename, message, key):
	img = Image.open(filename)

	while len(message) % 16 != 0:
		message=message + 'x'

	message = encodeAES(message,key)
	binary = str2bin(message) + '1111111111111110'
	if img.mode in ('RGBA'):
		img = img.convert('RGBA')
		dataimg = img.getdata()
		
		newData = []
		digit = 0
		temp = ''
		for item in dataimg:
			if (digit < len(binary)):
				newpix = encodeLSB(rgb2hex(item[0],item[1],item[2]),binary[digit])
				if newpix == None:
					newData.append(item)
				else:
					r, g, b = hex2rgb(newpix)
					newData.append((r,g,b,255))
					digit += 1
			else:
				newData.append(item)	
		img.putdata(newData)
		img.save(filename, "PNG")
		return "Selesai!"
			
	return "Mode gambar tidak cocok, tidak bisa di proses"

						
				

def retr(filename, key):
	img = Image.open(filename)
	binary = ''
	
	if img.mode in ('RGBA'): 
		img = img.convert('RGBA')
		dataimg = img.getdata()
		
		for item in dataimg:
			digit = decodeLSB(rgb2hex(item[0],item[1],item[2])) 
			if digit == None:
				pass	#next pixel
			else:
				binary = binary + digit
				if (binary[-16:] == '1111111111111110'):
					print "Success"
					binary = bin2str(binary[:-16])
					plain = decodeAES(binary,key)
					for x in plain:
						if plain[-1] == 'x':
							plain = plain[:-1]

					return plain

		return bin2str(binary) 

	return "Mode gambar tidak cocok, tidak bisa di proses"

def Main():
	parser = optparse.OptionParser('penggunaan program '+\
		'-e (enkripsi) atau -d (dekripsi) <file yang dituju>')
	parser.add_option('-e', dest='hide', type='string', \
		help='path file yang akan di enkripsi')
	parser.add_option('-d', dest='retr', type='string', \
		help='path file yang akan di dekripsi')
	
	(options, args) = parser.parse_args()
	if (options.hide != None):
		text = raw_input("Masukan pesan yang akan disembunyikan: ")
		password = raw_input("Masukan password: ")
		
		key = SHA256.new(password.encode('utf-8')).digest()
		print hide(options.hide, text,key)
	elif (options.retr != None):
		password = raw_input("Masukan password: ")
		
		key = SHA256.new(password.encode('utf-8')).digest()
        	print retr(options.retr,key)
	else:
		print parser.usage
		exit(0)


if __name__ == '__main__':
	Main()


