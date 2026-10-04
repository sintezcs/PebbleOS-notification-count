"""Fail CI before packaging if the native count API or source-base declaration drifted."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
state = json.loads((ROOT / 'custom/state.json').read_text())
expected = subprocess.check_output(['git','rev-parse',state['base_tag']+'^{commit}'],cwd=ROOT,text=True).strip()
assert expected == state['base_commit'], 'base tag no longer matches pinned commit'
spec = json.loads((ROOT/'tools/generate_native_sdk/exported_symbols.json').read_text())
def functions(exports):
    result=[]
    for item in exports:
        if item['type']=='group':result.extend(functions(item['exports']))
        elif item['type']=='function':result.append(item)
    return result
base_spec = json.loads(subprocess.check_output(
    ['git','show',state['base_tag']+':tools/generate_native_sdk/exported_symbols.json'],
    cwd=ROOT,text=True))
assert int(spec['revision']) > int(base_spec['revision']), 'private revision must follow upstream'
def ordered(exports):
    return sorted(functions(exports), key=lambda x: (int(x.get('addedRevision', 0)), x.get('sortName', x['name'])))
def abi_record(entry):
    fields=('name','addedRevision','sortName','implName','removed','internal','appOnly','workerOnly','skipDefinition')
    return {key:entry.get(key) for key in fields}
base_functions=ordered(base_spec['exports'])
custom_functions=ordered(spec['exports'])
assert [abi_record(x) for x in custom_functions[:len(base_functions)]] == [abi_record(x) for x in base_functions], 'upstream ABI prefix changed'
assert len(custom_functions)==len(base_functions)+1, 'unexpected extra private exports'
api = [x for x in functions(spec['exports']) if x['name']=='notification_service_peek_count']
assert len(api)==1 and int(api[0]['addedRevision'])==state['private_export_revision']
assert int(spec['revision'])==state['private_export_revision']
fw = ROOT/'src/fw' if (ROOT/'src/fw').is_dir() else ROOT/'fw'
info = (fw/'process_management/pebble_process_info.h').read_text()
minor = int(re.search(r'#define PROCESS_INFO_CURRENT_SDK_VERSION_MINOR\s+(0x[0-9a-fA-F]+|\d+)',info).group(1),0)
assert minor==state['private_sdk_minor']
header = (fw/'applib/notification_service.h').read_text()
assert 'uint32_t notification_service_peek_count(void);' in header
assert 'notification_storage_iterate(' in (fw/'syscall/notification_syscalls.c').read_text()
tests = (ROOT/'tests/fw/services/notifications/test_notification_storage.c').read_text()
for case in ('count_empty','count_retained_including_read','count_excludes_deleted','count_after_clear_and_store'):
    assert '__'+case+'(' in tests
print('Notification API, SDK version, pinned release and storage test contract verified.')
