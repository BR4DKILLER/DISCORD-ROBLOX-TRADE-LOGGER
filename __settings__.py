import json

def DoesFileExist(FileName):
    try:
        File = open(FileName, 'r')
        File.close()
        return True 
    except:
        return False
        
def GetFileContent(FileName):
    try:
        File = open(FileName, 'r')
        Content = File.read()
        File.close()
        return True, Content
    except:
        return False, 'File Does Not Exist'

def WriteSettings(FileName, Dictionary):
    try:
        File = open(FileName, 'w')
        json.dump(Dictionary, File, ensure_ascii=False, indent=4)
        File.close()
        return True, ('Wrote Dictionary as JSON in file ' + FileName)
    except Exception as Exc:
        return False, ('An Error Occured: ' + str(Exc))

def ReturnSettings(FileName):
    try:
        File = open(FileName, 'r')
        Content = File.read()
        Content = Content.replace('\'','"')
        Settings = json.loads(Content)
        File.close()
        return True, Settings
    except Exception as Exc:
        return False, ('An Error Occured: ' + str(Exc))
