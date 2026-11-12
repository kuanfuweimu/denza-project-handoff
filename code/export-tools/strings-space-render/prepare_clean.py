from pathlib import Path
p=Path(__file__).parent
s=(p/'reference_showcase.py').read_text(encoding='utf-8')
s=s.replace('strings-space_showcase_30s_4k60_reference_v2.mp4','strings-space_showcase_30s_4k60_subject_only.mp4').replace('reference-v2','subject-only')
needle="exec(compile(render_code,str(HERE/'render_check.py'),'exec'),globals())"
patch='''# Export-only isolation: keep lit dynamic strands, remove all stage draw calls.
render_code='\\n'.join(line for line in render_code.splitlines() if not any(token in line for token in ["structtex.use", "lines(.45", "fp,fv=programs['floor']", "fv.render", "dp,dv=programs['dot']", "for mirror in [.45,0.]"]))+'\\n'
assert all(token not in render_code for token in ["structtex.use", "lines(.45", "programs['floor']", "programs['dot']"])
'''
assert needle in s
s=s.replace(needle,patch+needle)
(p/'clean_showcase.py').write_text(s,encoding='utf-8')
print('Created export-only clean renderer')
