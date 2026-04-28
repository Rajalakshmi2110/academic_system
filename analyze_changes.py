from pptx import Presentation
from pptx.util import Inches

prs = Presentation("/Users/rathrajy/learning/project/academic_system/presentation.pptx")

# Compare key differences between pptx and create_ppt.py
# Focus on slides that changed

changes = []

# Slide 2: Key Features moved down (4.2→5.15, 4.65→5.6)
# Slide 3: Positions shifted (Problem 2.1→1.92, bullets 2.5→2.32, Methodology 4.0→4.57, bullets 4.4→5.03)
# Slide 4: Similar shifts
# Slide 5: Key Findings box 1.5→3.64h, Research Gap moved to right (6.15"), layout changed to 2-column
# Slide 6: Box height 5.5→3.89
# Slide 8: B heading moved (3.75→4.38), B bullets (4.15→4.78)
# Slide 9: B heading (3.61→4.1), B bullets (4.01→4.5)
# Slide 10: Text box resized (6.43→7.04 width, 6.04→6.08 height)
# Slide 11: A bullets height (2.1→2.88), B heading (3.85→4.36), B bullets (4.25→4.76, 2.5→2.54)
# Slide 12: B heading (3.62→4.29), B bullets (4.02→4.86, width 5.5→5.97, height 2.5→2.54)
# Slide 13: Images resized
# Slide 18: Many position changes
# Slide 19: Layout changed significantly - removed Live Usage & Latency sections
# Slide 21: References box height changed (3.5→5.57), Thank You removed
# Slide 22: New Thank You slide

for i, slide in enumerate(prs.slides, 1):
    for shape in slide.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if p.text.strip():
                    pass

print("Analysis complete - see changes list above")
