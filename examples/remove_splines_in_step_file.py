from spline_replacer import replace_splines

spline_free = replace_splines(
    solids="solid_with_spines.step",
    tolerance = 0.1,
    theAngularDeflection = 0.5,
    theCurvatureDeflection = 0.01,
)
spline_free.save("solid_without_splines.step")
