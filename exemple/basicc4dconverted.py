"""
08-26-2017
Basic exemple of the arnold python wrapper.
    It convert diffuse, first layer of reflectance, normal and alpha into a correct arnold shader.
"""

import c4d
import os

from arnold_wrapper.Arnold import Arnold

def get_reflectance(mat):
    """Get the texture inside the first slot the c4d reflectance channel"""
    filename = None

    base = c4d.REFLECTION_LAYER_LAYER_DATA + c4d.REFLECTION_LAYER_LAYER_SIZE * 4
    try:
        filename = mat[base + c4d.REFLECTION_LAYER_COLOR_TEXTURE]
    except:
        pass

    return filename

def get_normal(mat):
    """Get the texture inside the normal channel of a c4d mat"""
    filename = None

    try:
        filename = mat[c4d.MATERIAL_NORMAL_SHADER]
    except:
        pass

    return filename

def get_diffuse(mat):
    """Get the texture inside the diffuse channel of a c4d mat"""
    filename = None

    try:
        filename = mat[c4d.MATERIAL_COLOR_SHADER]
    except:
        pass

    return filename

def get_alpha(mat):
    """Get the texture inside the alpha channel of a c4d mat"""
    filename = None
    inverted = False

    try:
        filename = mat[c4d.MATERIAL_ALPHA_SHADER]
        inverted = mat[c4d.MATERIAL_ALPHA_INVERT]
    except:
        pass

    return filename, inverted

def past_assignment(doc, source, dest):
    """Copy assignement beetween source math to dest mat"""
    tag = None
    ObjLink = source[c4d.ID_MATERIALASSIGNMENTS]

    source_count = ObjLink.GetObjectCount()
    for i in range(0, source_count):
        tag = ObjLink.ObjectFromIndex(doc, i)

    if tag:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, tag)
        tag[c4d.TEXTURETAG_MATERIAL] = dest

def get_filepath(sha):
    """Get the file path of a Xbitmap"""
    if not sha:
        return None

    if not sha.CheckType(c4d.Xbitmap):
        return None

    full_path = sha[c4d.BITMAPSHADER_FILENAME]
    if not full_path:
        return None

    return str(full_path)

def convert_c4d_to_arnold(doc, mat):
    """Main function that convert c4d mat to arnold mat"""
    a = Arnold()

    #Get material data
    diffuse = get_diffuse(mat)
    diffuse_path = get_filepath(diffuse)

    reflectance = get_reflectance(mat)
    reflectance_path = get_filepath(reflectance)

    normal = get_normal(mat)
    normal_path = get_filepath(normal)

    alpha, alpha_invert = get_alpha(mat)
    alpha_path = get_filepath(alpha)


    #Create the new arnold shader
    new_mat = c4d.BaseMaterial(a.ARNOLD_MATERIAL)

    doc.InsertMaterial(new_mat)
    doc.AddUndo(c4d.UNDOTYPE_NEW, new_mat)

    #Copy the name
    new_mat.SetName(mat.GetName())

    #copy affectation
    past_assignment(doc, mat, new_mat)

    a.set_mat(new_mat)
    standard_node = a.create_shader(a.ARNOLD_SHADER_GV, "standard_surface", 700, 200)
    a.connect_beauty(standard_node.get_node(), 0)

    #Set Diffuse
    if diffuse_path:
        node_diffuse_pict = a.create_shader(a.ARNOLD_SHADER_GV, "image", 100, 100)
        node_diffuse_pict.set_parameter("image.filename", diffuse_path)
        node_diffuse_pict.get_node().SetName("Diff image")

        a.create_connection(node_diffuse_pict.get_node(), 0, standard_node.get_node(), "standard_surface.base_color")
    else:
        standard_node.set_parameter("standard_surface.base_color", mat[c4d.MATERIAL_COLOR_COLOR])

    #Set specular
    if reflectance_path:
        node_specular_pict = a.create_shader(a.ARNOLD_SHADER_GV, "image", 100, 200)
        node_specular_pict.set_parameter("image.filename", reflectance_path)
        node_specular_pict.get_node().SetName("Spec image")

        a.create_connection(node_specular_pict.get_node(), 0, standard_node.get_node(), "standard_surface.specular")
        a.create_connection(node_diffuse_pict.get_node(), 0, standard_node.get_node(), "standard_surface.specular_color")
    else:
        if diffuse_path:
            a.create_connection(node_diffuse_pict.get_node(), 0, standard_node.get_node(), "standard_surface.specular")
            a.create_connection(node_diffuse_pict.get_node(), 0, standard_node.get_node(), "standard_surface.specular_color")
        else:
            standard_node.set_parameter("standard_surface.specular", 0.5)

    #Set normal
    if normal_path:
        node_normal_pict = a.create_shader(a.ARNOLD_SHADER_GV, "image", 100, 300)
        node_normal_pict.set_parameter("image.filename", normal_path)
        node_normal_pict.get_node().SetName("Normal image")

        node_bump = a.create_shader(a.ARNOLD_SHADER_GV, "bump2d", 350, 300)
        node_bump.set_parameter("bump2d.bump_height", 0.1)

        a.create_connection(node_normal_pict.get_node(), 0, node_bump.get_node(), "bump2d.bump_map")

        a.create_connection(node_bump.get_node(), 0, standard_node.get_node(), "standard_surface.normal")

    #Set alpha
    if alpha_path:
        node_alpha_pict = a.create_shader(a.ARNOLD_SHADER_GV, "image", 100, 400)
        node_alpha_pict.set_parameter("image.filename", alpha_path)
        node_alpha_pict.get_node().SetName("Alpha image")

        if alpha_invert:
            node_invert_alpha = a.create_shader(a.ARNOLD_SHADER_GV, "complement", 350, 400)

            a.create_connection(node_alpha_pict.get_node(), 0, node_invert_alpha.get_node(), "complement.input")
            a.create_connection(node_invert_alpha.get_node(), 0, standard_node.get_node(), "standard_surface.opacity")
        else:
            a.create_connection(node_alpha_pict.get_node(), 0, standard_node.get_node(), "standard_surface.opacity")

def main():
    doc = c4d.documents.GetActiveDocument()
    if not doc: return

    doc.StartUndo()

    mats = doc.GetActiveMaterials()
    for mat in reversed(mats):
        buffer_mat = mat
        if mat.CheckType(c4d.Mmaterial):
            convert_c4d_to_arnold(doc, mat)
        doc.AddUndo(c4d.UNDOTYPE_DELETE, buffer_mat)
        buffer_mat.Remove()

    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()