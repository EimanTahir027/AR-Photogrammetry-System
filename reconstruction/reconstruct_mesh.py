import open3d as o3d
import numpy as np

PLY_IN  = 'reconstruction/sparse_points.ply'
OBJ_OUT = 'models/obj/model_mesh.obj'

import os; os.makedirs('models/obj', exist_ok=True)

print('Loading point cloud...')
pcd = o3d.io.read_point_cloud(PLY_IN)
print(f'  {len(pcd.points)} points loaded')

# Remove statistical outliers
print('Removing outliers...')
pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
print(f'  {len(pcd.points)} points after filtering')

# Estimate normals
print('Estimating normals...')
pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
pcd.orient_normals_consistent_tangent_plane(100)

# Poisson surface reconstruction
print('Running Poisson reconstruction...')
mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=9)

# Remove low-density vertices (boundary noise)
print('Cleaning mesh...')
densities = np.asarray(densities)
keep = densities > np.percentile(densities, 5)
mesh.remove_vertices_by_mask(~keep)
mesh.remove_degenerate_triangles()
mesh.remove_duplicated_triangles()
mesh.remove_duplicated_vertices()
mesh.compute_vertex_normals()

print(f'  Mesh: {len(mesh.vertices)} vertices, {len(mesh.triangles)} triangles')

print(f'Saving to {OBJ_OUT}...')
o3d.io.write_triangle_mesh(OBJ_OUT, mesh)
print('Done!')