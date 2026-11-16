from pathlib import Path
import os,json,subprocess,hashlib,configparser,re
from progress import prepare,backup
r=Path(__file__).resolve().parents[1]
if hashlib.sha256((r/'game/Rally/Rally.exe').read_bytes()).hexdigest()!='8eb7bdf01b8dc30ba40a43ac3d4065b9035cc59d58dd01b3c03113a1403171b5':raise SystemExit('Unsupported Rally.exe revision')
prepare()
for n in ['logs','compatdata']:(r/n).mkdir(exist_ok=True)
for name in ['Rally/config.ini','ShellData/ShellData.ini','ShellData/GameSettings.ini']:
 p=r/'game'/name
 c=configparser.ConfigParser(inline_comment_prefixes=(';',));c.optionxform=str;c.read_string(p.read_text())
 settings={'GameSettings':{'SPEEDO':'Km/h','LANGUAGE':'English','DIFFICULTY':'Easy'},'Network':{'Enabled':'0','CabinetID':'1'},'Credit':{'Freeplay':'1'}}
 if name=='Rally/config.ini':settings['Graphics']={'HorizontalResolution':'1920','VerticalResolution':'1080','VSync':'1','RefreshRate':'60'}
 for section,values in settings.items():
  if not c.has_section(section):c.add_section(section)
  for k,v in values.items():c.set(section,k,v)
 with p.open('w') as f:c.write(f)
env=os.environ.copy();env.update(json.loads((r/'source/runtime-env.json').read_text()))
env.update(STEAM_COMPAT_CLIENT_INSTALL_PATH=str(Path.home()/'.local/share/Steam'),STEAM_COMPAT_DATA_PATH=str(r/'compatdata'),PROTON_LOG='0',WINEDEBUG='-all',WAL_LOG='Z:'+str(r/'logs/payload.log').replace('/','\\'))
profile=(r/'dependencias/sega-rally-3.yaml').read_text()
match=re.search(r'^  WAL_EUROPAR_PATCHES_1920: \"([^\"]+)\"',profile,re.M)
if not match:raise SystemExit('Missing upstream 1080p profile')
env['WAL_EUROPAR_PATCHES_1920']=match.group(1)
env['DXVK_LOG_PATH']=str(r/'logs')
env['PROTON_LOG_DIR']=str(r/'logs')
env.pop('LD_PRELOAD',None)
with (r/'logs/controls.log').open('a') as log:
 helper=subprocess.Popen(['python3',str(r/'source/controls.py')],env=env,stdout=log,stderr=subprocess.STDOUT)
 try:
  with (r/'logs/session.log').open('a') as out:
   subprocess.run([str(Path.home()/'.local/share/Steam/compatibilitytools.d/GE-Proton11-12/proton'),'waitforexitandrun',str(r/'game/Rally/Rally.exe')],cwd=r/'game/Rally',env=env,stdout=out,stderr=subprocess.STDOUT)
 finally:
  helper.terminate();helper.wait(timeout=8);backup()
