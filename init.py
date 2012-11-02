import bpy
import mathutils
'''
!!! OCHE BYDLOCODE
'''
input = open('C:\\projects\\py_mod\\Book1.csv','rt')
data_list_str = input.readlines()
input.close()
data_list=[] # sfasf
str_pos=1
# A. Extract data from file (csv)
for data_def in data_list_str:
	if data_def[-1]=='\n':
		data_def=data_def[:-1]
	data_str=data_def.split(',')
	# get nessesary info from data
	# 1. Acceleration
	data_elem = []
	if data_str[0]=='accelerometer': # !!! data length
		# time
		data_elem.append(float(data_str[1]))
		# device
		data_elem.append('accelerometer')
		# parameters
		# value
		data_elem.append([float(data_str[-3]),float(data_str[-2]),float(data_str[-1])])
		data_list.append(data_elem)
	else:
		print('String ',str_pos,' has wrong structure:',data_def)
	str_pos=str_pos+1

# sort datalist by time
#data_list.sort(key=(lambda el : el[0])
	
# B. Positions and errors calculation
# time, position, orientation not implemented yet
curr_pos = [0.0, 0.0, 0.0]
curr_time = 0.0
curr_acc = [0.0, 0.0, 0.0]
curr_vel = [0.0, 0.0, 0.0]
curr_orient = [0.0, 0.0, 0.0]
veh_pos = []
veh_pos.append([curr_time,curr_pos[:]])
for data_value in data_list:
	if data_value[1]=='accelerometer':
		new_time = data_value[0]
		time_d = new_time - curr_time
		for coord in [0,1,2]:
			curr_pos[coord] = curr_pos[coord] + curr_vel[coord]*time_d + curr_acc[coord]*time_d*time_d/2
			curr_vel[coord] = curr_vel[coord] + curr_acc[coord]*time_d
			curr_acc[coord] = data_value[2][coord]
	curr_time = new_time
	veh_pos.append([curr_time,curr_pos[:]])

# C. Drawing
objects = []
factor = 0.2
for coord in veh_pos:
	bpy.ops.mesh.primitive_cube_add(location=(coord[1][0],coord[1][1],coord[1][2]))
	bpy.data.meshes[-1].transform(mathutils.Matrix.Scale(factor,4))
	objects.append(bpy.data.meshes[-1].name)
	