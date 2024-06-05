from spline_replacer import replace_splines

spline_free = replace_splines(
    solids="solid_with_splines.step",
    tolerance = 20,
    theAngularDeflection = 0.5,
    theCurvatureDeflection = 0.01,
)
spline_free.save("solid_without_splines.step")
