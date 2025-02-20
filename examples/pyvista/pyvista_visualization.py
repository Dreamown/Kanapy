#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example for visualization of microstructures with pyvista
Requires a pyvista installation in the knpy envirnment, e.g. with
(knpy) $ conda install -c conda-forge pyvista



@author: Alexander Hartmaier, ICAMS/Ruhr University Germany
August 2022
"""
import numpy as np
import kanapy as knpy
import pyvista as pv
from vtk import VTK_HEXAHEDRON

Nv = 40
size = 50
periodic = True
if periodic:
    name = 'pbc_px'
else:
    name = 'px'
matname = 'Simulanium fcc'
ms_elong = {'Grain type': 'Elongated', 
          'Equivalent diameter': {'std': 1.0, 'mean': 12.0, 'offs': 6.0, 'cutoff_min': 10.0, 'cutoff_max': 20.0},
          'Aspect ratio': {'std':1.5, 'mean': 1.7, 'offs': 0.8, 'cutoff_min': 1.0, 'cutoff_max': 3.0}, 
          'Tilt angle': {'std': 15., 'mean': 90., "cutoff_min": 0.0, "cutoff_max": 180.0}, 
          'RVE': {'sideX': size, 'sideY': size, 'sideZ': size, 'Nx': Nv, 'Ny': Nv, 'Nz': Nv}, 
          'Simulation': {'periodicity': str(periodic), 'output_units': 'um'},
          'Phase': {'Name': 'Simulanium fcc', 'Number': 0, 'Volume fraction': 1.0}}

ms = knpy.Microstructure(ms_elong)
ms.init_stats()
ms.init_RVE()
ms.pack()
ms.plot_ellipsoids()
ms.voxelize()
ms.plot_voxels()
ms.generate_grains()
ms.plot_grains()
ms.write_stl(file='{}_{}grains.stl'.format(name, ms.Ngr))


# generate pyvista grid of polyhedral grains
facets = set()
ptlbl = []
points = []
faces = []
f2gr = []
grains = ms.geometry['Grains']
for igr in grains.keys():
    for fc in grains[igr]['Simplices']:
        nds = ms.geometry['Vertices'][fc]
        facet = str(sorted(nds))
        if facet in facets:
            continue
        else:
            facets.add(facet)
        pts = ms.geometry['Points'][fc]
        faces.append(3)
        f2gr.append(igr)
        for pt in pts:
            ptl = str(pt)
            if ptl in ptlbl:
                faces.append(ptlbl.index(ptl))
            else:
                faces.append(len(points))
                points.append(pt)
                ptlbl.append(ptl)

poly_grid = pv.PolyData(points, faces)
poly_grid.cell_data['Grain'] = f2gr
pl = pv.Plotter()
pl.add_mesh(poly_grid, show_edges=True)
pl.add_point_labels(poly_grid.cell_centers(), 'Grain', font_size=24)
pl.show()

# generate pyvista grid for voxelated structure
nvox = ms.mesh.nvox
cells = np.ones((nvox, 9), dtype=int)*8
for iv, nodes in ms.mesh.voxel_dict.items():
    cells[iv-1, 1:9] = np.array(nodes) - 1
celltypes = np.empty(nvox, dtype=np.uint8)
celltypes[:] = VTK_HEXAHEDRON
vox_grid = pv.UnstructuredGrid(cells.ravel(), celltypes, ms.mesh.nodes)
vox_grid['Grains'] = ms.mesh.grains.ravel(order='F')
vox_grid.plot(show_edges=True)

# generate pyvista grid for smoothened structure
ms.smoothen()
smooth_grid = pv.UnstructuredGrid(cells.ravel(), celltypes, ms.mesh.nodes_smooth)
smooth_grid['Grains'] = ms.mesh.grains.ravel(order='F')
smooth_grid.plot(show_edges=True)
