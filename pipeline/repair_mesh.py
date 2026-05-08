import trimesh, numpy as np
from scipy.spatial import KDTree
import trimesh.repair, trimesh.smoothing

PLY_POINTS = 'reconstruction/sparse_points.ply'
PLY_MESH   = 'reconstruction/sparse_mesh.ply'
GLB_OUT    = 'models/glb/model.glb'
OBJ_OUT    = 'models/obj/model_mesh.obj'

def read_colored_ply(path):
    with open(path, 'rb') as f:
        while True:
            line = f.readline().decode('utf-8').strip()
            if line == 'end_header':
                break
            if line.startswith('element vertex'):
                n = int(line.split()[-1])
        data = np.frombuffer(f.read(n * 15), dtype=np.dtype([
            ('x','f4'),('y','f4'),('z','f4'),
            ('r','u1'),('g','u1'),('b','u1')
        ]))
    xyz = np.column_stack([data['x'], data['y'], data['z']])
    rgb = np.column_stack([data['r'], data['g'], data['b']]) / 255.0
    return xyz, rgb

print('Loading colored point cloud...')
pts_xyz, pts_rgb = read_colored_ply(PLY_POINTS)

print('Loading mesh...')
mesh = trimesh.load(PLY_MESH)
print(f'  Before: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces')

# Step 1: Remove degenerate geometry
print('Removing degenerate geometry...')
trimesh.repair.fix_winding(mesh)
trimesh.repair.fix_normals(mesh)

# Step 2: Keep only the largest connected component (removes floating junk)
print('Keeping largest component...')
components = mesh.split(only_watertight=False)
mesh = max(components, key=lambda m: len(m.faces))
print(f'  After cleanup: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces')

# Step 3: Very gentle smoothing only (2 iterations, low lambda)
print('Gentle smoothing (2 iterations)...')
trimesh.smoothing.filter_laplacian(mesh, lamb=0.1, iterations=2)
trimesh.repair.fix_normals(mesh)

# Step 5: Transfer colors from point cloud
print('Transferring colors...')
tree = KDTree(pts_xyz)
_, idx = tree.query(mesh.vertices, k=3, workers=-1)
# Average 3 nearest neighbors for smoother color
colors = (pts_rgb[idx].mean(axis=1) * 255).astype(np.uint8)
alpha = np.full((len(colors), 1), 255, dtype=np.uint8)
mesh.visual.vertex_colors = np.hstack([colors, alpha])

print(f'  Final: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces')

# Flip 180° around X axis to correct COLMAP's Y-down coordinate system
rotation = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
mesh.apply_transform(rotation)
trimesh.repair.fix_normals(mesh)
print('Orientation corrected.')

print(f'Saving GLB -> {GLB_OUT}')
mesh.export(GLB_OUT)
print(f'Saving OBJ -> {OBJ_OUT}')
mesh.export(OBJ_OUT)
print('Done!')