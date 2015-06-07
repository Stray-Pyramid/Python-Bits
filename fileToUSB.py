#! python2.7
# fileToUSB.py - Transfers the selected file to drives that have been plugged in while the script is running.

import win32api, os, time, math
import sys, shutil, threading

def convertByteToMegabyte(bytes):
	return round(bytes / float(1024**2), 2)

	
def convertByteToGigabyte(bytes):
	return round(bytes / float(1024**3), 2)

def getFreeDiskSpace(driveLetter):
	try:
		secPerClus, bytePerSec, freeClusters, _ = win32api.GetDiskFreeSpace(driveLetter)
		bytePerClus = secPerClus * bytePerSec
		print('Got disk Space')
		return bytePerClus * freeClusters
	except:
		return

	
def getDrives():
	drives = win32api.GetLogicalDriveStrings()
	return drives.split('\\\000')[:-1]

def fileTransfer(filePath, drive):
	fileName = os.path.basename(filePath)
	print('Beginning file transfer on drive ' + drive)
	print('Filename: ' + fileName)
	try:
		shutil.copy(filePath, drive + '//' + fileName)
		print(drive + ' transfer finished. Connect next USB.')
	except:
		print(drive + ' drive was interrupted before the transfer could complete!')
		

# Get File to transfer
fileToTransfer = ' '.join(sys.argv[1:])

if not fileToTransfer:
	print('Usage: fileToUSB.py fileDirectory')
	sys.exit()

if not os.path.isfile(fileToTransfer):
	print('Invalid Path!')
	sys.exit()

fileSize = os.path.getsize(fileToTransfer)
	
# Get size of file to transfer
print('File to upload: ' + fileToTransfer)
print('File Size: ' + str(convertByteToMegabyte(fileSize)) + 'MB')

# Get List of current drives
currentDrives = getDrives()

print('Ready to start')
time.sleep(5)

while True:
	#Get list of drives
	previousDrives = currentDrives
	currentDrives = getDrives()
	
	#Check for disconnected drives
	for drive in previousDrives:
		if drive not in currentDrives:
			print('USB ' + drive + ' disconnected')
	
	#Check for connected drives
	for drive in currentDrives:
		if drive not in previousDrives:
			print('USB ' + drive + ' connected')
			print('Has ' + str(convertByteToGigabyte(getFreeDiskSpace(drive))) + 'GB of free space')
			
			if getFreeDiskSpace(drive) < fileSize:
				print('Drive ' + drive + ' does not have enough space')
			elif os.path.isfile(drive + '//' + os.path.basename(fileToTransfer)) and os.path.getsize(drive + '//' + os.path.basename(fileToTransfer)) == fileSize:
				print('File already exists on drive')
			else:
				while True:
					choice = raw_input("Start file transfer on drive " + drive + "? (Y/N)\n>")
					if choice[0].upper() == 'Y':
						fileTransferThread = threading.Thread(target=fileTransfer, args=(fileToTransfer, drive))
						fileTransferThread.start()
						break
					elif choice[0].upper() == 'N':
						print('Gotcha.')
						break
					else:
						print('I did not understand.')
						
	time.sleep(1)