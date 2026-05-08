import numpy as np, trimesh
from scipy.spatial import KDTree

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
    return (np.column_stack([data['x'], data['y'], data['z']]),
            np.column_stack([data['r'], data['g'], data['b']]) / 255.0)

print('Loading data...')
pts_xyz, pts_rgb = read_colored_ply(PLY_POINTS)
mesh = trimesh.load(PLY_MESH)
print(f'  Points: {len(pts_xyz)}, Faces: {len(mesh.faces)}')

# --- Step 1: Remove large "hole-spanning" faces ---
# Compute the max edge length of every face
v = mesh.vertices
f = mesh.faces
e1 = np.linalg.norm(v[f[:,1]] - v[f[:,0]], axis=1)
e2 = np.linalg.norm(v[f[:,2]] - v[f[:,1]], axis=1)
e3 = np.linalg.norm(v[f[:,0]] - v[f[:,2]], axis=1)
max_edge = np.maximum(np.maximum(e1, e2), e3)

# Keep faces whose longest edge is below the 60th percentile
threshold = np.percentile(max_edge, 60)
print(f'  Edge threshold: {threshold:.4f}')
keep = max_edge < threshold
mesh.update_faces(keep)
mesh.remove_unreferenced_vertices()
print(f'  After edge filter: {len(mesh.faces)} faces')

# --- Step 2: Keep only the largest piece ---
parts = mesh.split(only_watertight=False)
mesh = max(parts, key=lambda m: len(m.faces))
print(f'  Largest component: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces')

# --- Step 3: Fix normals ---
trimesh.repair.fix_winding(mesh)
trimesh.repair.fix_normals(mesh)

# --- Step 4: Color from point cloud (avg 5 neighbours) ---
print('Applying colors...')
tree = KDTree(pts_xyz)
_, idx = tree.query(mesh.vertices, k=5, workers=-1)
colors = (pts_rgb[idx].mean(axis=1) * 255).astype(np.uint8)
mesh.visual.vertex_colors = np.hstack([colors, np.full((len(colors),1), 255, np.uint8)])

print(f'Saving...')
mesh.export(GLB_OUT)
mesh.export(OBJ_OUT)
print('Done!')