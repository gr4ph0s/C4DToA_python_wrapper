"""
09-02-2017
Exemple of the arnold python wrapper.
    Show how to get data from material and add shader / set parameter
"""

import c4d
from arnold_wrapper.Arnold import Arnold

def main():
    doc = c4d.documents.GetActiveDocument()
    if not doc: return

    doc.StartUndo()
    a = Arnold()

    mats = doc.GetActiveMaterials()
    for mat in mats:
        a.set_mat(mat)
        nodes_data = a.get_material_informations()

        # Get the node connected to the beauty port
        old_standard_node = nodes_data["beauty_node"]
        if old_standard_node is None:
            continue

        # Create standard material and set values
        new_standard_node = a.create_shader(a.ARNOLD_SHADER_GV, "standard_surface", 300, 600)
        new_standard_node.set_parameter(1044225467, c4d.Vector(0.161, 0.205, 0.23)) #diffuse color
        new_standard_node.set_parameter(2099493681, 0.21) #diffuse roughness
        new_standard_node.set_parameter(1046994997, 0.8) #spec weight
        new_standard_node.set_parameter(801517079, c4d.Vector(0.21, 0.186, 0.145)) #spec color
        new_standard_node.set_parameter(1876347704, c4d.Vector(0.21, 0.186, 0.145)) #spec color

        #Create user data substance
        user_data_node = a.create_shader(a.ARNOLD_SHADER_GV, "user_data_rgb", 300, 700)
        user_data_node.set_parameter(1215145447, "substance")

        #Create a mix node that will combine the 3 previous nodes
        mix_node = a.create_shader(a.ARNOLD_SHADER_GV, "mix_shader", 700, 300)

        #loop throught all connection to check if an alpha is in use or not
        for connection in nodes_data["all_connections"]:

            #Check if output port is linked to an opacity port
            if connection.output_port == a._hash_id("standard_surface.opacity"):
                print connection

                a.create_connection(connection.input_node.get_node(), 0,
                                    new_standard_node.get_node(), "standard_surface.opacity")
                break

        #Connect 3 node to the mix shader
        a.create_connection(old_standard_node.get_node(), 0, mix_node.get_node(), "mix_shader.shader1")
        a.create_connection(new_standard_node.get_node(), 0, mix_node.get_node(), "mix_shader.shader2")
        a.create_connection(user_data_node.get_node(), 0, mix_node.get_node(), "mix_shader.mix")

        #Connect mix to beauty
        a.disconnect_beauty()
        a.connect_beauty(mix_node.get_node(), 0)


    doc.EndUndo()
    c4d.EventAdd()


if __name__ == '__main__':
    main()