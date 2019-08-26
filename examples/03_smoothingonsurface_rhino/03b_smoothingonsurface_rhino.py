from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.datastructures import Mesh
from compas.geometry import smooth_area

import compas_rhino

from compas_rhino.helpers import mesh_from_guid

from compas_rhino.conduits import LinesConduit
from compas_rhino.geometry import RhinoSurface
from compas_rhino.artists import MeshArtist


# make a callback for pulling the free vertices back to the surface
# and update the conduit
# at every iteration

def callback(k, args):
    for index in range(len(xyz)):
        if index in fixed:
            continue
        x, y, z = surf.closest_point(xyz[index])
        xyz[index][0] = x
        xyz[index][1] = y
        xyz[index][2] = z

    conduit.lines = [[xyz[u], xyz[v]] for u, v in edges]
    conduit.redraw(k)


# make an artist for visualization
# and clear the output layer

artist = MeshArtist(None, layer='mesh-out')
artist.clear_layer()

# make a mesh datastructure from a Rhino mesh object
# and select a target surface

guid = compas_rhino.select_mesh()
mesh = mesh_from_guid(Mesh, guid)

guid = compas_rhino.select_surface()
surf = RhinoSurface(guid)

# extract the input for the smoothing algorithm from the mesh
# and identify the boundary as fixed

xyz       = mesh.get_vertices_attributes('xyz')
faces     = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
adjacency = [mesh.vertex_faces(key, ordered=True) for key in mesh.vertices()]
fixed     = set(mesh.vertices_on_boundary())

# make a conduit for visualization

edges = list(mesh.edges())
lines = [[xyz[i], xyz[j]] for i, j in edges]

conduit = LinesConduit(lines, refreshrate=5)

# with the conduit enabled
# run the smoothing algorithm

with conduit.enabled():
    smooth_area(
        xyz,
        faces,
        adjacency,
        fixed=fixed,
        kmax=100,
        callback=callback)

# update the mesh when smoothing is done

for key, attr in mesh.vertices(True):
    attr['x'] = xyz[key][0]
    attr['y'] = xyz[key][1]
    attr['z'] = xyz[key][2]

# draw the result

artist.mesh = mesh
artist.draw_mesh()
