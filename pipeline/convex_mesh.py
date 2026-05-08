import trimesh, numpy as np
from scipy.spatial import KDTree, ConvexHull

PLY_POINTS = 'reconstruction/sparse_points.ply'
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
print(f'  {len(pts_xyz)} points')

# Remove outliers (points far from the median)
median = np.median(pts_xyz, axis=0)
dists = np.linalg.norm(pts_xyz - median, axis=1)
threshold = np.percentile(dists, 95)
mask = dists < threshold
pts_xyz = pts_xyz[mask]
pts_rgb = pts_rgb[mask]
print(f'  {len(pts_xyz)} points after outlier removal')

# Build convex hull mesh (zero holes guaranteed)
print('Building convex hull mesh...')
hull = ConvexHull(pts_xyz)
vertices = pts_xyz[hull.vertices]
# remap faces to new vertex indices
old_to_new = {old: new for new, old in enumerate(hull.vertices)}
faces = np.array([[old_to_new[i] for i in face] for face in hull.simplices])

mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
trimesh.repair.fix_normals(mesh)
print(f'  {len(mesh.vertices)} vertices, {len(mesh.faces)} faces')

# Transfer colors: average 5 nearest point cloud neighbors per vertex
print('Applying colors...')
tree = KDTree(pts_xyz)
_, idx = tree.query(mesh.vertices, k=5, workers=-1)
colors = (pts_rgb[idx].mean(axis=1) * 255).astype(np.uint8)
alpha = np.full((len(colors), 1), 255, dtype=np.uint8)
mesh.visual.vertex_colors = np.hstack([colors, alpha])

print(f'Saving GLB -> {GLB_OUT}')
mesh.export(GLB_OUT)
print(f'Saving OBJ -> {OBJ_OUT}')
mesh.export(OBJ_OUT)
print('Done! No holes.')