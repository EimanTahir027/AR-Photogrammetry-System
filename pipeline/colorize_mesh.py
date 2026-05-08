import struct, numpy as np, trimesh
from scipy.spatial import KDTree

PLY_POINTS = 'reconstruction/sparse_points.ply'
PLY_MESH   = 'reconstruction/sparse_mesh.ply'
GLB_OUT    = 'models/glb/model.glb'
OBJ_OUT    = 'models/obj/model_mesh.obj'

def read_colored_ply(path):
    with open(path, 'rb') as f:
        # parse header
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
print(f'  {len(pts_xyz)} colored points')

print('Loading mesh...')
mesh = trimesh.load(PLY_MESH)
print(f'  {len(mesh.vertices)} vertices, {len(mesh.faces)} faces')

print('Transferring colors via nearest neighbour...')
tree = KDTree(pts_xyz)
_, idx = tree.query(mesh.vertices, k=1, workers=-1)
colors = (pts_rgb[idx] * 255).astype(np.uint8)
mesh.visual.vertex_colors = np.column_stack([colors, np.full(len(colors), 255, dtype=np.uint8)])

print(f'Saving GLB -> {GLB_OUT}')
mesh.export(GLB_OUT)
print(f'Saving OBJ -> {OBJ_OUT}')
mesh.export(OBJ_OUT)
print('Done! Model now has colour.')