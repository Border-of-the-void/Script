import os
import subprocess
import sys
from datetime import *


Source = '/volume1/photo/Test2'
Target = '/volume1/photo/Test/To'
PathMd5Sum = '/usr/bin/md5sum'
PathToLog = '/volume1/docker/SortScript/ScriptLog'
TargetInSource = True	
SortFolderName = 'Sort'
ExifToolLocation = '/usr/share/applications/ExifTool/exiftool'
TimeZone = 3 #Разница во времени в часах
NoInf = [datetime.strptime('0001-01-01 00:00:00','%Y-%m-%d %H:%M:%S')]
NowTime = datetime.now()
LogFileCreated = False




if len(sys.argv) > 1:
	if len(sys.argv) == 2:
		TargetInSource = True
		Source = sys.argv[1]
	elif len(sys.argv) == 3:
		Source = sys.argv[1]
		Target = sys.argv[2]
		if Source == Target: TargetInSource = True
	
	
def TFN (filename, ModifityDateTime):
    DateTimeFromName = ''
    IsWA = 0
    if '%20' in filename: filename = filename.replace('%20', '')
    for i in filename:
        if i.isdigit(): DateTimeFromName += i
    if 'WA' in filename:
        IsWA = 1
        DateTimeFromName = DateTimeFromName[:8] + ModifityDateTime.strftime("%H%M%S")
    try: DateTimeFromName = datetime.strptime(DateTimeFromName[0:14],'%Y%m%d%H%M%S')
    except: DateTimeFromName = datetime.strptime('0001-01-01 00:00:00','%Y-%m-%d %H:%M:%S')
    return DateTimeFromName, IsWA


def DTFE (FilePath, NoInf):
	ExifCreateDate = datetime.strptime('0001:01:01 00:00:00','%Y:%m:%d %H:%M:%S')
	ExifDateTimeOriginal = datetime.strptime('0001:01:01 00:00:00','%Y:%m:%d %H:%M:%S')	
	try: ExifCreateDate = datetime.strptime(str(subprocess.run(['/usr/share/applications/ExifTool/exiftool', '-CreateDate', FilePath], capture_output=True).stdout)[36:55], '%Y:%m:%d %H:%M:%S')
	except:pass
	try: ExifDateTimeOriginal = datetime.strptime(str(subprocess.run(['/usr/share/applications/ExifTool/exiftool', '-DateTimeOriginal', FilePath], capture_output=True).stdout)[36:55], '%Y:%m:%d %H:%M:%S')
	except:pass
	if ExifCreateDate in NoInf:return ExifDateTimeOriginal
	else:return ExifCreateDate


def GetPack (DateTimeFromExif, DateTimeFromName, NoInf, SortFolderName, ModifityDateTime, TargetInSource, dirpath, Target, IsWA, filename):
        Pack = ''
        if TargetInSource:
            if not(DateTimeFromExif in NoInf) and not(DateTimeFromName in NoInf) and DateTimeFromName.strftime("%Y%m%d") == DateTimeFromExif.strftime("%Y%m%d"): 
            	Pack = DateTimeFromName.strftime("%Y")  + '/'
            	if DateTimeFromExif != DateTimeFromName: 
            		Name = DateTimeFromExif.strftime("%Y%m%d_%H%M%S") + IsWA*'_WA' + '.' + filename.split('.')[-1].lower()
            		return dirpath + '/', Pack, Name
            if DateTimeFromName in NoInf and DateTimeFromExif in NoInf: Name =  ModifityDateTime.strftime("%Y%m%d_%H%M%S") + IsWA*'_WA' + '.' + filename.split('.')[-1].lower()
            elif DateTimeFromName in NoInf: Name = DateTimeFromExif.strftime("%Y%m%d_%H%M%S") + IsWA*'_WA' + '.' + filename.split('.')[-1].lower()
            else: Name = DateTimeFromName.strftime("%Y%m%d_%H%M%S") + IsWA*'_WA' + '.' + filename.split('.')[-1].lower()
            return dirpath + '/', Pack, Name
        else:
            if DateTimeFromExif in NoInf or DateTimeFromName in NoInf or DateTimeFromName.strftime("%Y%m%d") != DateTimeFromExif.strftime("%Y%m%d"): Pack = SortFolderName + '/'
            else: Pack = DateTimeFromName.strftime("%Y") + '/'
            if DateTimeFromName in NoInf and DateTimeFromExif in NoInf: Name =  ModifityDateTime.strftime("%Y%m%d_%H%M%S") + IsWA*'_WA' + '.' + filename.split('.')[-1].lower()
            elif DateTimeFromName in NoInf: Name = DateTimeFromExif.strftime("%Y%m%d_%H%M%S") + IsWA*'_WA' + '.' + filename.split('.')[-1].lower()
            else: Name = DateTimeFromName.strftime("%Y%m%d_%H%M%S") + IsWA*'_WA' + '.' + filename.split('.')[-1].lower()
            return Target + '/', Pack, Name


def WorkByPack(dirpath, dirnames):
	for i in dirpath.split('/'):
		if len(i) > 0 and i[0] == '@':return True
		if len(i) > 0 and i[0] == '.':return True
	return False
	
	
def WorkByName(filename):
	if not('.' in filename): return True
	if filename == '.stignore': return True
	return False


def BashChangeDate(ExifToolLocation, Adress, ExifTime, TouchTime):
	FirstBashCommand = "'" + ExifToolLocation + "'" + ' -c -DateTimeOriginal=' + ExifTime +  ' -CreateDate=' + ExifTime + ' -ModifyDate=' + ExifTime + ' ' + Adress + ' -overwrite_original'
	os.system(FirstBashCommand)
	SecondBashCommand = "touch -m -a -t " + TouchTime + ' ' + Adress
	os.system(SecondBashCommand)	


for dirpath, dirnames, filenames in os.walk(Source):
	if WorkByPack(dirpath, dirnames): continue
	for filename in filenames:
		FilePath = os.path.join(dirpath, filename)
		if WorkByName(filename): continue
		try:
			DateOfFolder = datetime.strptime(dirpath.split('/')[-1][:10],'%Y-%m-%d')
			DateOfFile = datetime.strptime(filename[:8],'%Y%m%d')
			if DateOfFolder != DateOfFile:
				TimeOfFile = datetime.strptime(filename[9:15],'%H%M%S')
				Name = DateOfFolder.strftime("%Y%m%d") + filename[8:]
				BashChangeDate(ExifToolLocation, "'" + FilePath + "'", '"' + (DateOfFolder.strftime("%Y%m%d ") + TimeOfFile.strftime("%H%M%S"))+"+03:00" + '"', datetime.strptime(Name[:15], '%Y%m%d_%H%M%S').strftime('%Y%m%d%H%M.%S'))
				os.chdir(dirpath)
				os.rename(filename, Name) 
			if TargetInSource: continue
		except: pass
		SourceMd5 = ''
		TargetMd5 = ''
		ModifityDateTime = datetime.utcfromtimestamp(int(os.stat(dirpath).st_mtime) + TimeZone*3600)
		DateTimeFromExif = DTFE(FilePath, NoInf)
		DateTimeFromName, IsWA = TFN(filename, ModifityDateTime)
		Path, OlderPack, Name = GetPack(DateTimeFromExif, DateTimeFromName, NoInf, SortFolderName, ModifityDateTime, TargetInSource, dirpath, Target, IsWA, filename)
		PossiblePack = Name[0:4] + '-' + Name[4:6] + '-' + Name[6:8]
		MD5 = ['0', '1']
		while os.path.isfile(Path + OlderPack + PossiblePack + '/' + Name):
			PossiblePack = Name[0:4] + '-' + Name[4:6] + '-' + Name[6:8]
			FullPath = Path + OlderPack + PossiblePack
			BashChangeDate(ExifToolLocation, "'" + FilePath + "'", '"' + datetime.strptime(Name[:15], '%Y%m%d_%H%M%S').strftime('%Y:%m:%d %H:%M:%S')+"+03:00" + '"', datetime.strptime(Name[:15], '%Y%m%d_%H%M%S').strftime('%Y%m%d%H%M.%S'))
			MD5 [0] = subprocess.run([PathMd5Sum, FilePath], capture_output=True)
			MD5 [1] = subprocess.run([PathMd5Sum, FullPath], capture_output=True)
			SourceMd5 = str(MD5[0].stdout).split(' ')[0][2:]
			TargetMd5 = str(MD5[1].stdout).split(' ')[0][2:]
			if SourceMd5 == TargetMd5: break
			DateTime, Format = Name.split('.')
			DateTime = datetime.strptime(DateTime[:15],'%Y%m%d_%H%M%S') + timedelta(seconds = 1)
			Name = DateTime.strftime("%Y%m%d_%H%M%S" + '_WA' * IsWA + '.' + Format)
			if OlderPack != '/' and OlderPack != SortFolderName + '/': OlderPack = DateTime.strftime("%Y") + '/'
		FullPath = Path + OlderPack + PossiblePack
		BashChangeDate(ExifToolLocation, "'" + FilePath + "'", '"' + datetime.strptime(Name[:15], '%Y%m%d_%H%M%S').strftime('%Y:%m:%d %H:%M:%S')+"+03:00" + '"', datetime.strptime(Name[:15], '%Y%m%d_%H%M%S').strftime('%Y%m%d%H%M.%S'))
		if WorkByName(Name): continue
		os.system("mkdir -p " + "'" + FullPath + "'")
		BashCommand = "mv '" + FilePath +  "' '" + FullPath + '/' + Name + "'"
		os.system(BashCommand)
		OutputLogString = 'Путь ' + dirpath + ';' + 'Имя файла ' + filename + ';' + 'Дата модификации ' + ModifityDateTime.strftime('%Y-%m-%d_%H%M%S') + ';' + 'Дата экзифа ' + DateTimeFromExif.strftime('%Y-%m-%d_%H%M%S') + ';' + 'Дата из имени ' + DateTimeFromName.strftime('%Y-%m-%d_%H%M%S') + ';' + 'МД5 ресурса ' + SourceMd5 + ';' + 'МД5 цели ' + TargetMd5 + ';' + 'ISWA ' + str(IsWA) + ';' + 'Полный путь ' + FullPath + ';' + 'Имя ' + Name
		if LogFileCreated == False:
			f = open(PathToLog + '_' + NowTime.strftime("%Y%m%d_%H%M%S") + '.csv', 'w')
			LogFileCreated = True
		f.write(OutputLogString+'\n')
	if dirpath != Source:
		try: os.rmdir(dirpath)
		except: pass
if LogFileCreated: f.close()