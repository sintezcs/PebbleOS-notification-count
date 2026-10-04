"""Verify and collect a paired Time 2 PBZ/PBW artifact set."""
import hashlib
import json
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from package_firmware import package_firmware

root=Path.cwd()
state=json.loads((root/'custom/state.json').read_text())
slot=int(sys.argv[1]);build=root/'build';out=root/'artifacts';out.mkdir(exist_ok=True)
commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
base=state['base_tag']
sources=list(build.glob(f'normal_obelix_pvt_*_slot{slot}.pbz'))
assert len(sources)==1,sources
report=package_firmware(sources[0],out/f'PebbleOS-{base}-notifications-pvt-slot{slot}.pbz',root,int(time.time()),base,commit)
pbw=root/'custom/watchface/build/release.pbw'
with zipfile.ZipFile(pbw) as z:
    assert z.testzip() is None
    assert not any(n.endswith('.map') for n in z.namelist())
(out/'LCD221-matching-firmware.pbw').write_bytes(pbw.read_bytes())
report.update(base_tag=base,base_commit=state['base_commit'],custom_commit=commit,watchface_version=state['watchface_version'],physical_device_tested=False)
(out/f'verification-slot{slot}.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'INSTALL.txt').write_text('Select a system watchface (such as TicToc) before upgrading. Determine the running firmware slot and install the opposite-slot PVT image. After firmware finishes, install the paired LCD221 PBW from this same verified artifact set. Never mix a PBW from another firmware/SDK build. Physical validation remains necessary after installation.\n')
files=sorted(p for p in out.iterdir() if p.is_file() and not p.name.startswith('SHA256'))
(out/f'SHA256SUMS-slot{slot}').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
print(json.dumps(report,indent=2))
