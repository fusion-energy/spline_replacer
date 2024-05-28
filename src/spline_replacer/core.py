from pathlib import Path
import typing
import cadquery as cq
import numpy as np
from cadquery import importers
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from cadquery.occ_impl import shapes
import OCP

def facet_wire(
    wire,
    tolerance: float = 1e-3,
):
    """Converts specified curved edge types from a wire into a series of
    straight lines (facetets) with the provided tol (tolerance).

    Args:
        wire (cadquery.Wire): The CadQuery wire to select edge from which will
            be redraw as a series of straight lines (facet).
        facet_splines: If True then spline edges will be faceted. Defaults
            to True.
        facet_splines: If True then circle edges will be faceted.Defaults
            to True.
        tolerance: faceting toleranceto use when faceting cirles and
            splines. Defaults to 1e-3.

    Returns:
        cadquery.Wire
    """
    new_edges = []

    types_to_facet = ["BSPLINE", "BEZIER"]

    if isinstance(wire, cq.occ_impl.shapes.Edge):
        # this is for when a edge is passed
        edges = [wire]
    elif isinstance(wire, cq.occ_impl.shapes.Wire):
        # this is for imported stp files
        edges = wire.Edges()
    else:
        # this is for cadquery generated solids
        edges = wire.val().Edges()

    new_edges = []
    for edge in edges:
        if edge.geomType() in types_to_facet:
            print('spline or bezier edge found')
            new_edges.extend(transform_curve(edge, tolerance=tolerance).Edges())
        else:
            # print('not spline edge')
            new_edges.append(edge)

    # new_wire = cq.Wire(new_edges)
    new_wires = cq.occ_impl.shapes.edgesToWires(new_edges)
    new_new_wires = []
    for new_wire in new_wires:
        new_new_wires.append(new_wire.close())
    return new_new_wires

def transform_curve(edge, tolerance: float = 1e-3):
    """Converts a curved edge into a series of straight lines (facetets) with
    the provided tolerance.

    Args:
        edge (cadquery.Wire): The CadQuery wire to redraw as a series of
            straight lines (facet)
        tolerance: faceting tolerance to use when faceting cirles and
            splines. Defaults to 1e-3.

    Returns:
        cadquery.Wire
    """

    curve = edge._geomAdaptor()  # adapt the edge into curve
    start = curve.FirstParameter()
    end = curve.LastParameter()

    points = GCPnts_QuasiUniformDeflection(curve, tolerance, start, end)
    verts = (cq.Vector(points.Value(i + 1)) for i in range(points.NbPoints()))

    return cq.Wire.makePolygon(verts, close=True)

import cadquery as cq

solid = cq.Workplane().text(txt='G', fontsize=10, distance=1)

# for edge in solid.val().Edges():
all_new_wires = []
# for i,wire in enumerate(solid.val().Wires()):
#     new_wires = facet_wire(wire)
#     all_new_wires.append(new_wires)
    # cq.Face.makeFromWires(new_wires)

for face in solid.val().Faces():
    for w, wire in enumerate(face.wires()):
        print(w)
        new_wires = facet_wire(wire)

new_face = cq.occ_impl.shapes.wiresToFaces(new_wires)

import OCP

shell = OCP.TopoDS.TopoDS_Shell()
bldr = OCP.BRep.BRep_Builder()
bldr.MakeShell(shell)
for face in new_face:
    bldr.Add(shell, face.wrapped)
s = cq.Solid.makeSolid(cq.Shell(shell))
s.exportStep('desplined.stp')


# import OCP

# shell = OCP.TopoDS.TopoDS_Shell()
# bldr = OCP.BRep.BRep_Builder()
# bldr.MakeShell(shell)

# for face in solid.val().Faces():
#     new_wires_in_face = []
#     for w, wire in enumerate(face.wires()):
#         print(w)
#         new_wires = facet_wire(wire)
#         new_wires_in_face.extend(new_wires)
#     # new_face = cq.Face.makeFromWires(new_wires_in_face)
#     new_face = cq.occ_impl.shapes.wiresToFaces(new_wires_in_face)
#     bldr.Add(shell, new_face.wrapped)