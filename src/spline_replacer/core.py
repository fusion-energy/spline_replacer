import typing

import cadquery as cq
from OCP import BRepAdaptor, GCPnts
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeFilling
from OCP.GeomAbs import GeomAbs_C0
from OCP.ShapeAnalysis import ShapeAnalysis_FreeBounds
from OCP.TopTools import TopTools_HSequenceOfShape


def makeNSidedSurface(
    face,
    edges,
    continuity=GeomAbs_C0,
    degree=2,
    nbPtsOnCur=15,
    nbIter=2,
    anisotropy=False,
    tol2d=0.00001,
    tol3d=0.0001,
    tolAng=0.01,
    tolCurv=0.1,
    maxDeg=8,
    maxSegments=9,
):

    n_sided = BRepOffsetAPI_MakeFilling(
        degree,
        nbPtsOnCur,
        nbIter,
        anisotropy,
        tol2d,
        tol3d,
        tolAng,
        tolCurv,
        maxDeg,
        maxSegments,
    )
    for edge in edges:
        n_sided.Add(edge.wrapped, continuity)

    n_sided.LoadInitSurface(face)
    n_sided.Build()
    face = n_sided.Shape()
    return cq.Shape.cast(face).fix()


# def replace_splines(
#     solids: typing.Union[cq.Workplane, cq.Assembly],
#     tolerance: float = 0.1,
#     theAngularDeflection: float = 0.5,
#     theCurvatureDeflection: float = 0.01,
# ):
    

# spline_free_solid = replace_splines(assembly)

def replace_splines(
    solids: typing.Union[cq.Workplane, cq.Assembly],
    tolerance: float = 0.1,
    theAngularDeflection: float = 0.5,
    theCurvatureDeflection: float = 0.01,
):

    spine_free_assembly = cq.Assembly()

    if isinstance(solids, cq.Workplane):
        s_iterator = [solids]
    elif isinstance(solids, cq.Assembly):
        s_iterator= [s for s in solids.toCompound()]
        
    for solid in s_iterator:
        new_faces = []
        if hasattr(solid, 'val'):
            face_iterator = solid.val().Faces()
        else:
            face_iterator = solid.Faces()

        for face in face_iterator:
            spline_found = False
            edges = []
            for e in face.edges():
                if e.geomType() == "BSPLINE":
                    new_line_edges = GCPnts.GCPnts_TangentialDeflection(
                        BRepAdaptor.BRepAdaptor_Curve(e.wrapped),
                        theAngularDeflection=theAngularDeflection,
                        theCurvatureDeflection=theCurvatureDeflection,
                    )
                    if new_line_edges.NbPoints() > 1:
                        for i in range(2, new_line_edges.NbPoints() + 1):
                            p_0 = new_line_edges.Value(i - 1)
                            p_1 = new_line_edges.Value(i)
                            edge = cq.Edge.makeLine(
                                cq.Vector(p_0.X(), p_0.Y(), p_0.Z()),
                                cq.Vector(p_1.X(), p_1.Y(), p_1.Z()),
                            )
                            edges.append(edge)
                    spline_found = True
                else:
                    edges.append(e)

            if spline_found == True:
                wire = cq.Wire.combine(edges)
                # todo replace with try except with something that finds if the wire is planar
                try:
                    new_face = cq.occ_impl.shapes.wiresToFaces([wire[0].close()])
                    new_faces.append(new_face[0])
                except:

                    # edges to wires
                    wires_out = TopTools_HSequenceOfShape()
                    edges_in = TopTools_HSequenceOfShape()
                    for el in edges:
                        edges_in.Append(el.wrapped)
                    ShapeAnalysis_FreeBounds.ConnectEdgesToWires_s(
                        edges_in, 1e-6, False, wires_out
                    )

                    wires = [cq.Shape.cast(el) for el in wires_out]

                    bldr = BRepBuilderAPI_MakeFace(wires[0].wrapped, False)

                    for w in wires[1:]:
                        bldr.Add(w.wrapped)

                    bldr.Build()
                    if bldr.IsDone():
                        spine_face_with_straight_edges = cq.Shape.cast(bldr.Shape())
                    else:
                        spine_face_with_straight_edges = makeNSidedSurface(
                            face.wrapped, wires[0].Edges(), degree=2
                        )

                    tess = spine_face_with_straight_edges.tessellate(tolerance=tolerance)
                    for triangle in tess[1]:
                        # todo check if these should be clockwise or anticlockwise
                        edge1 = cq.Edge.makeLine(tess[0][triangle[0]], tess[0][triangle[1]])
                        edge2 = cq.Edge.makeLine(tess[0][triangle[1]], tess[0][triangle[2]])
                        edge3 = cq.Edge.makeLine(tess[0][triangle[0]], tess[0][triangle[2]])
                        wire = cq.Wire.combine([edge1, edge2, edge3])
                        new_face = cq.occ_impl.shapes.wiresToFaces([wire[0].close()])
                        new_faces.append(new_face[0])

            else:
                new_faces.append(face)

        sh = cq.Shell.makeShell(new_faces)
        spline_free_solid = cq.Solid.makeSolid(sh)
        spine_free_assembly.add(spline_free_solid)
    return spine_free_assembly





solid1 = (
    cq.Workplane("XY")
    .polyline([(1, 1), (1, 2)])
    .spline([(1, 2), (2, 4), (3, 2)])
    .polyline([(3, 2), (3, 1)])
    .threePointArc((2, 0), (1, 1))
    .close()
    .extrude(1)
)

cq.exporters.export(solid1, "solid1_with_spines.step")
spline_free_solid = replace_splines(solid1)
spline_free_solid.save("solid_without_spines.step")


solid2 = (
    cq.Workplane("XY")
    .polyline([(1, 1), (1, 2)])
    .spline([(1, 2), (2, 4), (3, 2)])
    .polyline([(3, 2), (3, 1)])
    .threePointArc((2, 0), (1, 1))
    .close()
    .extrude(-1)
)
cq.exporters.export(solid2, "solid2_with_spines.step")


assembly = cq.Assembly()
assembly.add(solid1)
assembly.add(solid2)
spline_free_assembly = replace_splines(assembly)
spline_free_assembly.save("assembly_without_spines.step")