import cadquery as cq


s = cq.Workplane("XY")
sPnts = [
    (2.75, 1.5),
    (2.5, 1.75),
    (2.0, 1.5),
    (1.5, 1.0),
    (1.0, 1.25),
    (0.5, 1.0),
    (0, 1.0),
]
r = s.lineTo(3.0, 0).lineTo(3.0, 1.0).spline(sPnts, includeCurrent=True).close()
solid1 = r.extrude(0.5)

# contains no splines
solid2 = cq.Workplane("XY").box(15, 15, 0.5).faces(">Z").workplane().hole(9)

assembly = cq.Assembly()
assembly.add(solid1)
assembly.add(solid2)
assembly.save("one_solid_with_spine_one_solid_without_spline.step")

from spline_replacer import replace_splines

spline_free = replace_splines(
    solids=assembly,
    tolerance=20,
    theAngularDeflection=0.5,
    theCurvatureDeflection=0.01,
)
spline_free.save("two_solids_without_splines.step")
