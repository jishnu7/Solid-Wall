# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_addon_info = {
    'name': 'Add Mesh: Solid Wall',
    'author': 'Jishnu <jishnu7@gmail.com>',
    'version': '0.1',
    'blender': (2, 52, 5),
    'location': 'View3D > Add > Mesh > Wall',
    'description': 'Soli wall mesh',
    'category': 'Add Mesh'}

__bpydoc__ = """
Solid Wall

This add-on is mainly aimed at architects. Architects can easily create wall using this
add-on, they need not to waste time to correct the cut length at both sides.

Usage:

This mesh can be accessed via the "Add Mesh" menu in 3D View.

Version history:

v0.1 - Initial revision. Seems to work fine for most purposes.

TODO

* Convet a selected plane to a wall

""""
import bpy
from bpy.props import *

def create_mesh_object(context, verts, edges, faces, name, edit):

    # Get the current scene
    scene = context.scene
    
    # Get the active object.
    obj_act = scene.objects.active

    # Can't edit anything, unless we have an active obj.
    if edit and not obj_act:
        return None

    # Create new mesh
    mesh = bpy.data.meshes.new(name)

    # Make a mesh from a list of verts/edges/faces.
    mesh.from_pydata(verts, edges, faces)

    # Update mesh geometry after adding stuff.
    mesh.update()

    # Deselect all objects.
    bpy.ops.object.select_all(action='DESELECT')

    if edit:
        # Replace geometry of existing object

        # Use the active obj and select it.
        ob_new = obj_act
        ob_new.selected = True

        if obj_act.mode == 'OBJECT':
            # Get existing mesh datablock.
            old_mesh = ob_new.data

            # Set object data to nothing
            ob_new.data = None

            # Clear users of existing mesh datablock.
            old_mesh.user_clear()

            # Remove old mesh datablock if no users are left.
            if (old_mesh.users == 0):
                bpy.data.meshes.remove(old_mesh)

            # Assign new mesh datablock.
            ob_new.data = mesh

    else:
        # Create new object
        ob_new = bpy.data.objects.new(name, mesh)

        # Link new object to the given scene and select it.
        scene.objects.link(ob_new)
        ob_new.selected = True

        # Place the object at the 3D cursor location.
        ob_new.location = context.scene.cursor_location

    if obj_act and obj_act.mode == 'EDIT':
        if not edit:
            # We are in EditMode, switch to ObjectMode.
            bpy.ops.object.mode_set(mode='OBJECT')

            # Select the active object as well.
            obj_act.selected = True

            # Apply location of new object.
            scene.update()

            # Join new object into the active.
            bpy.ops.object.join()

            # Switching back to EditMode.
            bpy.ops.object.mode_set(mode='EDIT')

            ob_new = obj_act

    else:
        # We are in ObjectMode.
        # Make the new object the active one.
        scene.objects.active = ob_new

    return ob_new

def setup_mesh(l, w, h):

    verts = [
            (-l-w,-w/2,-h),
            (-l,-w/2,-h),
            (l,-w/2,-h),
            (l+w,-w/2,-h),
            (l+w,-w/2,h),
            (l,-w/2,h),
            (-l,-w/2,h),
            (-l-w,-w/2,h),
            (-l-w,w/2,-h),
            (-l,w/2,-h),
            (l,w/2,-h),
            (l+w,w/2,-h),
            (l+w,w/2,h),
            (l,w/2,h),
            (-l,w/2,h),
            (-l-w,w/2,h)
            ]
    faces = [
            [0,1,6,7],
            [0,8,15,7],
            [0,1,9,8],
            [14,15,8,9],
            [14,15,7,6],
            [14,13,10,9],
            [14,13,5,6],
            [2,5,6,1],
            [2,10,9,1],
            [2,3,4,5],
            [2,3,11,10],
            [12,13,10,11],
            [12,13,5,4],
            [12,4,3,11]
            ]

    return verts, faces


class Wall(bpy.types.Operator):
    bl_idname = "mesh.primitive_wall_add"
    bl_label = "Add Wall"
    bl_options = {'REGISTER', 'UNDO'}

    # edit - Whether to add or update.
    edit = BoolProperty(name="",
        description="",
        default=False,
        options={'HIDDEN'})
        
    length = FloatProperty(name = "Length",
           attr = "length",
           description="Length of the wall",
           default = 1.0, min = 0.01, max = 10.0)
    width = FloatProperty(name = "Width",
           description="Width of the wall",
           attr = "width",
           default = 0.25, min = 0.01, max = 10.0)
    height = FloatProperty(name = "Height",
           attr = "height",
           description="Height of the wall",
           default = 0.5, min = 0.01, max = 10.0)
           
    def execute(self, context):
        props = self.properties
        verts, faces = setup_mesh(props.length,
            props.width,
            props.height)

        obj = create_mesh_object(context, verts, [], faces,
            "Wall", props.edit)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}

import space_info

menu_func = (lambda self,
            context: self.layout.operator(Wall.bl_idname,
            text="Wall", icon="FACESEL"))

def register():
    # Register the operators/menus.
    bpy.types.register(Wall)

    # Add "Wall" menu to the "Add Mesh" menu
    space_info.INFO_MT_mesh_add.append(menu_func)


def unregister():
    # Unregister the operators/menus.
    bpy.types.unregister(Wall)

    # Remove "Wall" menu from the "Add Mesh" menu.
    space_info.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
