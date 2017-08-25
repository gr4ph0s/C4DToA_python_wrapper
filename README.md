# C4DToA_python_wrapper
Wrapper class for the current API of Arnold for c4d

## Class Presentation

### Arnold
**Arnold class is the main wrapper. You normally only have to deal with it.**
- set_mat, **Make sure to call it before any others one.** Set on which material change are done.
- get_material_infromations, return dict of data from a material
- create_shader, create a shader inside the material
- remove_shader, remove a shader inside the material
- create_connection, create a connection beetween 2 node and 2 port_id
- remove_connection, remove a connection from a node, port_id
- connect_beauty, connect node to the beauty port
- connect_displacement, connect node to the displacement port
- connect_viewport, connect viewport to the viewport port
- disconnect_beauty, discconnect node to the beauty port
- disconnect_displacement, discconnect node to the displacement port
- discconnect_viewport, discconnect viewport to the viewport port

### Node
**Node class represent a c4d.modules.graphview.GvNode inside an arnold shader network.**
- get_node, return the c4d.modules.graphview.GvNode attached to the Node object
- get_type, return the Arnold type of the node
- get_parameter, get the value of a parameter from id/name
- set_parameter, set the value of a parameter from id/name

### Connection
**Connection class represent a connection inside an arnold shader network.**

### Message
**Message wrap the current arnold API. Basic workflow set_data => send => get_data, You normally never have to deal with this class**
- set_data, set the data for the message to be send
- send, send the message
- get_data, retrieve data from previous

## Examples
Basic exemple for create an arnold material, a standard node link to the beauty and a user_data_rgb linked to the weight color of the standard.
```
import c4d
from arnold_wrapper.Arnold import Arnold

#define wrapper
arnold = Arnold()

#create arnold material
mat = c4d.BaseMaterial(arnold.ARNOLD_MATERIAL)
doc.InsertMaterial(mat)

#Define the mat where we gonna act after
arnold.set_mat(mat)

#create user_data_rgb
user_data_rgb = arnold.create_shader(arnold.ARNOLD_SHADER_GV, "user_data_rgb", 200, 200)
user_data_rgb.set_parameter("user_data_rgb.default", c4d.Vector(0.2,0.4,0.6))

#create our standard node
standard_node = arnold.create_shader(arnold.ARNOLD_SHADER_GV, "standard_surface", 600, 200)

#create connections
arnold.create_connection(user_data_rgb.get_node(), 0, standard_node.get_node(), "standard_surface.base_color")
arnold.connect_beauty(standard_node.get_node(), 0)

c4d.EventAdd()
```

### Installation
Even if you could do basic import I suggest you to read 
[Best Practice For Imports from official support forum](http://www.plugincafe.com/forum/forum_posts.asp?TID=10727)
and then use 
[py-localimport](https://gist.github.com/NiklasRosenstein/f5690d8f36bbdc8e5556) from [Niklas Rosenstein](https://github.com/NiklasRosenstein)

### Compatibility
Tested and build on C4dToA 2.0+ and R17/R18
