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
    facet_splines: bool = True,
    facet_circles: bool = True,
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
    edges = []

    types_to_facet = []
    if facet_splines:
        types_to_facet.append("BSPLINE")
    if facet_circles:
        types_to_facet.append("CIRCLE")

    if isinstance(wire, cq.occ_impl.shapes.Edge):
        # this is for when a edge is passed
        iterable_of_wires = [wire]
    elif isinstance(wire, cq.occ_impl.shapes.Wire):
        # this is for imported stp files
        iterable_of_wires = wire.Edges()
    else:
        # this is for cadquery generated solids
        iterable_of_wires = wire.val().Edges()

    for edge in iterable_of_wires:
        if edge.geomType() in types_to_facet:
            edges.extend(transform_curve(edge, tolerance=tolerance).Edges())
        else:
            edges.append(edge)

    return edges

def transform_curve(edge, tolerance: float = 1e-3):
    """Converts a curved edge into a series of straight lines (facetets) with
    the provided tolerance.

    Args:
        edge (cadquery.Wire): The CadQuery wire to redraw as a series of
            straight lines (facet)
        tolerance: faceting toleranceto use when faceting cirles and
            splines. Defaults to 1e-3.

    Returns:
        cadquery.Wire
    """

    curve = edge._geomAdaptor()  # adapt the edge into curve
    start = curve.FirstParameter()
    end = curve.LastParameter()

    points = GCPnts_QuasiUniformDeflection(curve, tolerance, start, end)
    verts = (cq.Vector(points.Value(i + 1)) for i in range(points.NbPoints()))

    return cq.Wire.makePolygon(verts)

import cadquery as cq

cq.Workplane.text("G")