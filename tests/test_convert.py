import cadquery as cq
from spline_replacer import replace_splines, contains_splines


solid1 = (
    cq.Workplane("XY")
    .polyline([(1, 1), (1, 2)])
    .spline([(1, 2), (2, 4), (3, 2)])
    .polyline([(3, 2), (3, 1)])
    .threePointArc((2, 0), (1, 1))
    .close()
    .extrude(1)
)
solid2 = (
    cq.Workplane("XY")
    .polyline([(1, 1), (1, 2)])
    .spline([(1, 2), (2, 4), (3, 2)])
    .polyline([(3, 2), (3, 1)])
    .threePointArc((2, 0), (1, 1))
    .close()
    .extrude(-1)
)


def test_workplane_convert():
    assert contains_splines(solid1) == True

    spline_free_solid = replace_splines(solid1)

    assert contains_splines(spline_free_solid) == False


def test_assembly_convert():

    assembly = cq.Assembly()
    assembly.add(solid1)
    assembly.add(solid2)
    spline_free_assembly = replace_splines(assembly)

    assert contains_splines(spline_free_assembly) == False
    assert contains_splines(assembly) == True


def test_stp_file():

    spline_free = replace_splines("tests/solid_with_spines.step")

    assert contains_splines(spline_free) == False

    solid_with_splines = cq.importers.importStep("tests/solid_with_spines.step")
    assert contains_splines(solid_with_splines) == True
