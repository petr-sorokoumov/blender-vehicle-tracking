import bpy
import mathutils
'''
!!! OCHE BYDLOCODE
'''
input = open('/usr/share/extra/projects/blender-vehicle-tracking/test/results.csv','rt')
data_list_str = input.readlines()
input.close()
data_list=[] # data as list of values
input_file_device_mapping = {'1':'accelX','2':'accelY','3':'accelZ','7':'rf'}
input_file_device_keys = list(input_file_device_mapping.keys())
str_pos = 0

# A0. Measurement units
accel_to_standard = 1
time_to_standard = 0.001
rfdata_to_standard = 0.01

# A. Extract data from file (csv)
for data_def in data_list_str:
    if data_def[-1]=='\n':
        data_def=data_def[:-1]
    data_str=data_def.split(';')
    # get nessesary info from data
    # If there is data in string, process it
    if len(data_str)>2 and data_str[1] in list(input_file_device_keys):
        # 1. Acceleration
        data_elem = []
        if (input_file_device_mapping[data_str[1]] in ['accelX','accelY','accelZ']) and (len(data_str)==12):
            # time
            data_elem.append(float(data_str[3])*time_to_standard)
            # device
            data_elem.append(input_file_device_mapping[data_str[1]])
            # parameters --- now value only; TODO errors
            # value
            data_elem.append(float(data_str[2])*accel_to_standard)
            data_list.append(data_elem)
            # 2. Range finder
        elif input_file_device_mapping[data_str[1]] == 'rf' and (len(data_str)==12):
            # time
            data_elem.append(float(data_str[3])*time_to_standard)
            # device
            data_elem.append('rf')
            # parameters --- now value only; TODO errors
            # value
            data_elem.append(float(data_str[2])*rfdata_to_standard)
            data_list.append(data_elem)
        else:
            print('Input: string', str_pos,'with operation', data_str[1],'has wrong structure:',data_def)
    else:
        print('Input: string ',str_pos,' has wrong structure:',data_def)
    str_pos=str_pos+1

# sort datalist by time
data_list.sort(key=(lambda el : el[0]))
	
# B. Positions and errors calculation
# position, orientation not implemented yet
curr_pos = [0.0, 0.0, 0.0]
curr_time = 0.0
pos_diff_time = 0.0
last_moment_pos = [0.0, 0.0, 0.0] # position of robot in last moment when new data were read
curr_acc = [0.0, 0.0, 0.0]
curr_vel = [0.0, 0.0, 0.0]
curr_orient = [0.0, 0.0]
veh_pos = {}
veh_pos[curr_time] = curr_pos[:]
pos_indices = {'accelX':0,'accelY':1,'accelZ':2}

# range finder data
rf_indices = {'rf':0}
obstacles = []

for data_value in data_list:
    new_time = data_value[0]
    # B1. Acceleration
    if data_value[1] in pos_indices.keys():
        new_index = pos_indices[data_value[1]]
        # if data for this moment is already in container, update it
        if new_time==curr_time:
            # calculate new data for coordinate under question
            curr_pos[new_index] = curr_pos[new_index] + curr_vel[new_index]*pos_diff_time + curr_acc[new_index]*pos_diff_time*pos_diff_time/2
            curr_vel[new_index] = curr_vel[new_index] + curr_acc[new_index]*pos_diff_time
            curr_acc[new_index] = data_value[2]
            veh_pos[curr_time][new_index]=curr_pos[new_index]
        else: # if the moment is new, add data for all coordinates to container
            pos_diff_time = new_time - curr_time
            for coord in [0,1,2]:
                curr_pos[coord] = curr_pos[coord] + curr_vel[coord]*pos_diff_time + curr_acc[coord]*pos_diff_time*pos_diff_time/2
                curr_vel[coord] = curr_vel[coord] + curr_acc[coord]*pos_diff_time
            curr_acc[new_index] = data_value[2]
            curr_time = new_time
            veh_pos[curr_time] = curr_pos[:]
    elif data_value[1] in rf_indices.keys():
        # calculate current position and add obstacle near this position
        pos_now = [0,0,0]
        rf_diff_time = new_time - curr_time
        for coord in [0,1,2]:
                pos_now[coord] = curr_pos[coord] + curr_vel[coord]*rf_diff_time + curr_acc[coord]*rf_diff_time*rf_diff_time/2
        # now direction is fixed on 0X. TODO direction and rfposition processing
        obstacles.append([pos_now[0]-data_value[2], pos_now[1], pos_now[2]])
    else:
        print('Processor:',data_value,'has unknown type and will not be processed')

# C. Drawing
#if objects not in vars():
objects = []
# drawing settings
vehicle_scale = 0.1 # height ~ 20 cm
coord_scale = 1
time_scale = 1/time_to_standard # measurements per time unit in input data
# ordering by timestamps
times_keys = list(veh_pos.keys())[:]
times_keys.sort()
# add mesh for vehicle
vehicle_mesh_coords=[(0.0, 0.0, 1.0), (1.0, -1.0, -1.0), (1.0, 1.0 ,-1.0), \
(-1.0, 1.0,-1.0), (-1.0, -1.0, -1.0)]
vehicle_mesh_faces = [(0,1,2,0),(0,2,3,0),(0,3,4,0),(0,4,1,0),(1,2,3,4)]
vehicle_mesh = bpy.data.meshes.new('Vehicle_mesh')
vehicle_obj = bpy.data.objects.new('Vehicle',vehicle_mesh)
vehicle_obj.location = Vector((0,0,0))
bpy.context.scene.objects.link(vehicle_obj)
vehicle_mesh.from_pydata(vehicle_mesh_coords,[],vehicle_mesh_faces)
vehicle_mesh.update(calc_edges = True)
# vehicle scaling
vehicle_mesh.transform(mathutils.Matrix.Scale(vehicle_scale,4))
# initial position
vehicle_matrix_pos = mathutils.Matrix.Identity(4)
vehicle_matrix_rot = mathutils.Matrix.Identity(4)
vehicle_obj.keyframe_insert(data_path="location", frame=times_keys[0]*time_scale, index=0)
vehicle_obj.keyframe_insert(data_path="location", frame=times_keys[0]*time_scale, index=1)
vehicle_obj.keyframe_insert(data_path="location", frame=times_keys[0]*time_scale, index=2)
for timestamp in times_keys:
    coord = veh_pos[timestamp]
    print (coord)
    vehicle_obj.keyframe_insert(data_path="location", frame=timestamp*time_scale, index=0)
    vehicle_obj.keyframe_insert(data_path="location", frame=timestamp*time_scale, index=1)
    vehicle_obj.keyframe_insert(data_path="location", frame=timestamp*time_scale, index=2)
    vehicle_obj.location = Vector((coord[0]*coord_scale,coord[1]*coord_scale,coord[2]*coord_scale))

# obstacle drawing (static, post-factum) TODO Add appearance
obstacle_mesh_coords = [(0,-1,0),(0,0,1),(0,1,0),(0,0,-1)]
obstacle_mesh_faces = [(0,1,2,3)]
curr = 1
for pos in obstacles:
    obst_mesh = bpy.data.meshes.new('Obstacle%d_mesh' % curr)
    obst_obj = bpy.data.objects.new('Obstacle%d' % curr, obst_mesh)
    obst_obj.location = Vector((pos[0],pos[1],pos[2]))
    bpy.context.scene.objects.link(obst_obj)
    obst_mesh.from_pydata(obstacle_mesh_coords,[],obstacle_mesh_faces)
    obst_mesh.update(calc_edges = True)
    curr = curr + 1

