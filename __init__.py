from . datavec import *
import mathutils
from bpy.props import (StringProperty, BoolProperty,
                       IntProperty, FloatProperty, FloatVectorProperty)
from math import *

import numpy
from sympy import *
import math
import bpy
bl_info = {
    "name": "KMathAddon",
    "blender": (3, 0, 0),
    "category": "Object",
}




def monobj(nom, vert, edg, face, loc, smooth, uvname, uvd):
    new_mesh = bpy.data.meshes.new(nom)
    new_mesh.from_pydata(vert, edg, face)
    new_mesh.update()
    new_object = bpy.data.objects.new(name=nom, object_data=new_mesh)
    # position rotation scale
    new_object.location = loc
    new_object.rotation_euler = (0.0, 0.0, 0.0)
    new_object.scale = (1.0, 1.0, 1.0)
    for i, polygon in enumerate(new_object.data.polygons):
        polygon.use_smooth = (True if smooth[i] else False)
    new_uv = new_object.data.uv_layers.new(name=uvname)
    for loop in new_object.data.loops:
        new_uv.data[loop.index].uv = uvd[loop.index]
    new_object.data.update()
    return new_object


def vect(vec, vecf, context):

    # COLLECTION
    Koll = bpy.data.collections.new('chvect')
    sc = bpy.data.collections.new('vect')
    Koll.children.link(sc)
    bpy.data.scenes["Scene"].collection.children.link(Koll)

    orig = bpy.data.objects.new('orig', None)
    sc.objects.link(orig)
    norme = monobj('norme', vertices0, edges0, faces0,
                   vec, smooth_data0, 'CarteUV', uv_xy0)
    norme.parent = orig
    sc.objects.link(norme)

    flech = monobj('fv', vertices1, edges1, faces1,
                   vecf, smooth_data1, 'CarteUV', uv_xy1)
    flech.parent = orig
    fc = flech.constraints.new('TRACK_TO')
    fc.track_axis = 'TRACK_NEGATIVE_Z'
    fc.target = orig
    nc = norme.constraints.new('TRACK_TO')
    nc.track_axis = 'TRACK_Z'
    nc.target = flech
    drv = norme.driver_add('scale', 2)
    var = drv.driver.variables.new()
    var.name = 'MaVar'
    var.type = 'LOC_DIFF'
    var.targets[0].id = orig
    var.targets[1].id = flech
    drv.driver.expression = var.name + '-0.1'
    sc.objects.link(flech)

    fl = monobj('tu', vertices2, edges2, faces2,
                (0.0, 0.0, 1.0), smooth_data2, 'CarteUV', uv_xy2)
    fl.parent = flech
    fc = fl.constraints.new('TRACK_TO')
    fc.track_axis = 'TRACK_NEGATIVE_Z'
    fc.target = orig
    drv = fl.driver_add('location', 2)
    var = drv.driver.variables.new()
    var.name = 'MaVar'
    var.type = 'LOC_DIFF'
    var.targets[0].id = orig
    var.targets[1].id = flech
    drv.driver.expression = var.name + '*-1.0 +1'
    sc.objects.link(fl)
    orig.location = vec[:]
    
    bpy.ops.object.select_all(action='DESELECT')

    flech.select_set(True)
    bpy.context.view_layer.objects.active = flech
    return [orig, flech, fl]


def update_func(self, context):
    print("my test function", self)


def nettoi(name, bname):
    for cur in bpy.data.curves:
        if bname in cur.name:
            bpy.data.curves.remove(cur)
    for o in bpy.data.objects:
        if bname in o.name:
            bpy.data.objects.remove(o)
    for c in bpy.data.collections:
        if 'MaCollection' in c.name:
            bpy.data.collections.remove(c)




def update_fonc(self, context):
    x, y, z = symbols("x y z")

    equationc = self.equationc
    if equationc:
        try:
            name = 'fonction'
            bname = 'fonction'
            nettoi(name, bname)
            #bpy.data.orphans_purge()
            MaColl = bpy.data.collections.new('MaCollection'+name)
            context.scene.collection.children.link(MaColl)
            curveData = bpy.data.curves.new(name, type='CURVE')
            curveData.dimensions = '3D'
            curveData.resolution_u = 2
            curveData.bevel_depth = 0.01
            curveOB = bpy.data.objects.new(name, curveData)
            MaColl.objects.link(curveOB)
            n = 200
            yVals = []
            xVals = numpy.linspace(-5,5,n)
            zoom = 1
            exp = parse_expr(equationc)
            for xv in xVals:
                yVals.append((zoom*xv,0.0,zoom*exp.subs(x,xv),1))
            bpy.data.curves[name].splines.new('POLY')
            p = bpy.data.curves[name].splines[0].points
            p.add(len(yVals)-1)
            print(yVals)
            for i, coord in enumerate(yVals):
                p[i].co = coord
        except:
            import traceback
            print("", traceback.format_exc(limit=1))
    else:
        print("No expression is given")


class MesProps(bpy.types.PropertyGroup):
    equationc: bpy.props.StringProperty(name="Equation", description="Equation for y=f(x)", default="x", update=update_fonc)
    vect: bpy.props.FloatVectorProperty(name='Vect', description='', default=(0.0, 0.0, 0.0))
    vect1: bpy.props.FloatVectorProperty(name='Vect1', description='', default=(0.0, 0.0, 2.0), update=update_func)


class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_label = "Operateur Vectoriel"
    bl_idname = "object.simple_operator"

    def execute(self, context):
        vec = context.scene.mes_props.vect
        vecf = context.scene.mes_props.vect1
        vect(vec, vecf, context)
        return {'FINISHED'}


class HelloWorldPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Mon Panel Vectoriel"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MathVectoriel"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Calcul Vectoriel", icon='WORLD_DATA')
        row = layout.row()
        moprop = row.prop(context.scene.mes_props, "vect")
        moprop1 = row.prop(context.scene.mes_props, "vect1")
        moneq = row.prop(context.scene.mes_props, "equationc")
        row = layout.row()
        monop = row.operator("object.simple_operator")


classes = [MesProps, SimpleOperator, HelloWorldPanel]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mes_props = bpy.props.PointerProperty(type=MesProps)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
