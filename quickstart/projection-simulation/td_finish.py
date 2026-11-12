M = op("/project1/mapping_denza")
M.par.Videofile = r"D:/Codex/workspace/tengshi-projection/td_assets/test_pattern_bright.png"
M.par.Source = "video"
t = M.op("text_readme")
add = ("- Projection preview: null_sim_preview (Preview page: Orbit, Tilt, Distance, Wall Brightness, Shadows)\n"
"- Playback: HAP Q or H.265 at 7680x1656 both measured 60 fps on RTX 4080 Laptop; use transcode.ps1\n")
if "Projection preview" not in t.text:
    t.text = t.text + add
print(M.par.Source.eval(), M.op("null_content").width)
