# Adds a Source menu (Template / Video File / Spout / TOP) to /project1/mapping_denza.
M = op("/project1/mapping_denza")
NULL_BLUE = (0.1843137255, 0.3490196078, 0.6784313725)
pg = [p for p in M.customPages if p.name == "Mapping"][0]
if not hasattr(M.par, "Source"):
    s = pg.appendMenu("Source", label="Content Source")[0]
    s.menuNames = ["template", "video", "spout", "top"]
    s.menuLabels = ["UV Template", "Video File", "Spout (Arena etc.)", "Content TOP"]
    pg.appendFile("Videofile", label="Video File")
    pg.appendStr("Spoutname", label="Spout Sender Name")
    pg.sort("Source", "Videofile", "Spoutname", "Content", "Testpattern", "Blackout")
for old in ("moviefilein_content", "spoutin_content", "switch_source"):
    if M.op(old):
        M.op(old).destroy()
vid = M.create(moviefileinTOP, "moviefilein_content")
vid.nodeX, vid.nodeY = -200, 520
vid.par.file.expr = "parent().par.Videofile"
vid.viewer = True
sp = M.create(spoutinTOP, "spoutin_content")
sp.nodeX, sp.nodeY = -200, 380
sp.viewer = True
sp_par = [p.name for p in sp.pars("*name*")]
for cand in ("sendername", "spoutname", "name"):
    if hasattr(sp.par, cand):
        getattr(sp.par, cand).expr = "parent().par.Spoutname"
        break
sel = M.op("select_content")
sel.par.top.expr = "parent().par.Content.eval() or 'moviefilein_uv_template'"
sw = M.create(switchTOP, "switch_source")
sw.nodeX, sw.nodeY = 0, 520
sw.viewer = True
sw.inputConnectors[0].connect(M.op("moviefilein_uv_template"))
sw.inputConnectors[1].connect(vid)
sw.inputConnectors[2].connect(sp)
sw.inputConnectors[3].connect(sel)
sw.par.index.expr = "parent().par.Source.menuIndex"
# fit everything to the 7680x1656 unfolded canvas
fit = M.op("fit_canvas") or M.create(fitTOP, "fit_canvas")
fit.nodeX, fit.nodeY = 200, 520
fit.viewer = True
fit.par.outputresolution = "custom"
fit.par.resolutionw, fit.par.resolutionh = 7680, 1656
fit.inputConnectors[0].connect(sw)
old_sw = M.op("switch_content")
old_sw.par.index.expr = "int(parent().par.Testpattern)"
old_sw.inputConnectors[0].connect(fit)
M.par.Source = "template"
M.par.Spoutname = "Arena"
print("spout pars", sp_par)
print("ok", [o.name for o in (vid, sp, sw, fit)], old_sw.inputs[0].name, M.op("null_content").width, M.op("null_content").height)
