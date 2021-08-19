import os
from typing import List, Union, Tuple

import bpy

from external.vhacd.decompose import convex_decomposition
from src.utility.EntityUtility import Entity
import numpy as np
from mathutils import Vector, Matrix

from src.utility.Utility import Utility

from src.utility.MaterialUtility import Material

import bmesh
import mathutils

class MeshObject(Entity):

    def __init__(self, object: bpy.types.Object):
        super().__init__(object)

    @staticmethod
    def create_from_blender_mesh(blender_mesh: bpy.types.Mesh, object_name: str = None) -> "MeshObject":
        """ Creates a new Mesh object using the given blender mesh.

        :param blender_mesh: The blender mesh.
        :param object_name: The name of the new object. If None is given, the name of the given mesh is used.
        :return: The new Mesh object.
        """
        # link this mesh inside of a new object
        obj = bpy.data.objects.new(blender_mesh.name if object_name is None else object_name, blender_mesh)
        # link the object in the collection
        bpy.context.collection.objects.link(obj)
        return MeshObject(obj)

    @staticmethod
    def create_with_empty_mesh(object_name: str, mesh_name: str = None) -> "MeshObject":
        """ Creates an object with an empty mesh.
        :param object_name: The name of the new object.
        :param mesh_name: The name of the contained blender mesh. If None is given, the object name is used.
        :return: The new Mesh object.
        """
        if mesh_name is None:
            mesh_name = object_name
        return MeshObject.create_from_blender_mesh(bpy.data.meshes.new(mesh_name), object_name)

    @staticmethod
    def create_primitive(shape: str, **kwargs) -> "MeshObject":
        """ Creates a new primitive mesh object.

        :param shape: The name of the primitive to create. Available: ["CUBE"]
        :return:
        """
        if shape == "CUBE":
            bpy.ops.mesh.primitive_cube_add(*kwargs)
        elif shape == "CYLINDER":
            bpy.ops.mesh.primitive_cylinder_add(*kwargs)
        elif shape == "CONE":
            bpy.ops.mesh.primitive_cone_add(*kwargs)
        elif shape == "PLANE":
            bpy.ops.mesh.primitive_plane_add(*kwargs)
        elif shape == "SPHERE":
            bpy.ops.mesh.primitive_uv_sphere_add(*kwargs)
        elif shape == "MONKEY":
            bpy.ops.mesh.primitive_monkey_add(*kwargs)
        else:
            raise Exception("No such shape: " + shape)

        return MeshObject(bpy.context.object)

    @staticmethod
    def convert_to_meshes(blender_objects: list) -> List["MeshObject"]:
        """ Converts the given list of blender objects to mesh objects

        :param blender_objects: List of blender objects.
        :return: The list of meshes.
        """
        return [MeshObject(obj) for obj in blender_objects]

    def get_materials(self) -> List[Material]:
        """ Returns the materials used by the mesh.

        :return: A list of materials.
        """
        return Material.convert_to_materials(self.blender_obj.data.materials)

    def has_materials(self):
        return len(self.blender_obj.data.materials) > 0

    def set_material(self, index: int, material: Material):
        """ Sets the given material at the given index of the objects material list.

        :param index: The index to set the material to.
        :param material: The material to set.
        """
        self.blender_obj.data.materials[index] = material.blender_obj

    def add_material(self, material: Material):
        """ Adds a new material to the object.

        :param material: The material to add.
        """
        self.blender_obj.data.materials.append(material.blender_obj)

    def new_material(self, name: str):
        """ Creates a new material and adds it to the object.

        :param name: The name of the new material.
        """
        new_mat = Material.create(name)
        self.add_material(new_mat)
        return new_mat

    def clear_materials(self):
        """ Removes all materials from the object. """
        self.blender_obj.data.materials.clear()

    def replace_materials(self, material: bpy.types.Material):
        """ Replaces all materials of the object with the given new material.

        :param material: A material that should exclusively be used as new material for the object.
        """
        # first remove all existing
        self.clear_materials()
        # add the new one
        self.add_material(material)

    def duplicate(self):
        """ Duplicates the object.

        :return: A new mesh object, which is a duplicate of this object.
        """
        new_entity = self.blender_obj.copy()
        new_entity.data = self.blender_obj.data.copy()
        bpy.context.collection.objects.link(new_entity)
        return MeshObject(new_entity)

    def get_mesh(self) -> bpy.types.Mesh:
        """ Returns the blender mesh of the object.

        :return: The mesh.
        """
        return self.blender_obj.data

    def set_shading_mode(self, mode: str, angle_value: float = 30):
        """ Sets the shading mode of all faces of the object.

        :param mode: Desired mode of the shading. Available: ["FLAT", "SMOOTH", "AUTO"]. Type: str
        :param angle_value: Angle in degrees at which flat shading is activated in `AUTO` mode. Type: float
        """
        if mode.lower() == "flat":
            is_smooth = False
            self.blender_obj.data.use_auto_smooth = False
        elif mode.lower() == "smooth":
            is_smooth = True
            self.blender_obj.data.use_auto_smooth = False
        elif mode.lower() == "auto":
            is_smooth = True
            self.blender_obj.data.use_auto_smooth = True
            self.blender_obj.data.auto_smooth_angle = np.deg2rad(angle_value)
        else:
            raise Exception("This shading mode is unknown: {}".format(mode))

        for face in self.get_mesh().polygons:
            face.use_smooth = is_smooth

    def move_origin_to_bottom_mean_point(self):
        """
        Moves the object center to bottom of the bounding box in Z direction and also in the middle of the X and Y
        plane, which then makes the placement easier.
        """
        bpy.ops.object.select_all(action='DESELECT')
        self.select()
        bpy.context.view_layer.objects.active = self.blender_obj
        bb = self.get_bound_box()
        bb_center = np.mean(bb, axis=0)
        bb_min_z_value = np.min(bb, axis=0)[2]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.transform.translate(value=[-bb_center[0], -bb_center[1], -bb_min_z_value])
        bpy.ops.object.mode_set(mode='OBJECT')
        self.deselect()
        bpy.context.view_layer.update()

    def get_bound_box(self, local_coords: bool = False) -> np.ndarray:
        """
        :return: 8x3 array describing the object aligned bounding box coordinates in world coordinates
        """
        if not local_coords:
            return np.array([self.blender_obj.matrix_world @ Vector(cord) for cord in self.blender_obj.bound_box])
        else:
            return np.array([Vector(cord) for cord in self.blender_obj.bound_box])

    def persist_transformation_into_mesh(self, location: bool = True, rotation: bool = True, scale: bool = True):
        """
        Apply the current transformation of the object, which are saved in the location, scale or rotation attributes
        to the mesh and sets them to their init values.

        :param location: Determines whether the object's location should be persisted.
        :param rotation: Determines whether the object's rotation should be persisted.
        :param scale: Determines whether the object's scale should be persisted.
        """
        bpy.ops.object.transform_apply({"selected_editable_objects": [self.blender_obj]}, location=location, rotation=rotation, scale=scale)

    def get_origin(self) -> np.ndarray:
        """ Returns the origin of the object.

        :return: The origin in world coordinates.
        """
        return np.array(self.blender_obj.location.copy())

    def set_origin(self, point: Union[list, np.ndarray, Vector] = None, mode: str = "POINT") -> np.ndarray:
        """ Sets the origin of the object.

        This will not change the appearing pose of the object, as the vertex locations experience the inverse transformation applied to the origin.

        :param point: The point in world coordinates to which the origin should be set. This parameter is only relevent if mode is set to "POINT".
        :param mode: The mode specifying how the origin should be set. Available options are: ["POINT", "CENTER_OF_MASS", "CENTER_OF_VOLUME"]
        :return: The new origin in world coordinates.
        """
        context = {"selected_editable_objects": [self.blender_obj]}

        if mode == "POINT":
            if point is None:
                raise Exception("The parameter point is not given even though the mode is set to POINT.")
            prev_cursor_location = bpy.context.scene.cursor.location
            bpy.context.scene.cursor.location = point
            bpy.ops.object.origin_set(context, type='ORIGIN_CURSOR')
            bpy.context.scene.cursor.location = prev_cursor_location
        elif mode == "CENTER_OF_MASS":
            bpy.ops.object.origin_set(context, type='ORIGIN_CENTER_OF_MASS')
        elif mode == "CENTER_OF_VOLUME":
            bpy.ops.object.origin_set(context, type='ORIGIN_CENTER_OF_VOLUME')
        else:
            raise Exception("No such mode: " + mode)

        return self.get_origin()

    def enable_rigidbody(self, active: bool, collision_shape: str = 'CONVEX_HULL', collision_margin: float = 0.001, collision_mesh_source: str = "FINAL", mass: float = None, mass_factor: float = 1, friction: float = 0.5, angular_damping: float = 0.1, linear_damping: float = 0.04):
        """ Enables the rigidbody component of the object which makes it participate in physics simulations.

        :param active: If True, the object actively participates in the simulation and its key frames are ignored. If False, the object still follows its keyframes and only acts as an obstacle, but is not influenced by the simulation.
        :param collision_shape: Collision shape of object in simulation. Default: 'CONVEX_HULL'. Available: 'BOX', 'SPHERE', 'CAPSULE', 'CYLINDER', 'CONE', 'CONVEX_HULL', 'MESH', 'COMPOUND'.
        :param collision_margin: The margin around objects where collisions are already recognized. Higher values improve stability, but also make objects hover a bit.
        :param collision_mesh_source: Source of the mesh used to create collision shape. Default: 'FINAL'. Available: 'BASE', 'DEFORM', 'FINAL'.
        :param mass: The mass in kilogram the object should have. If None is given the mass is calculated based on its bounding box volume and the given `mass_factor`.
        :param mass_factor: Scaling factor for mass. This is only considered if the given `mass` is None. Defines the linear function mass=bounding_box_volume*mass_factor (defines material density).
        :param friction: Resistance of object to movement.
        :param angular_damping: Amount of angular velocity that is lost over time.
        :param linear_damping: Amount of linear velocity that is lost over time.
        """
        # Enable rigid body component
        bpy.ops.rigidbody.object_add({'object': self.blender_obj})
        # Sett attributes
        rigid_body = self.blender_obj.rigid_body
        rigid_body.type = "ACTIVE" if active else "PASSIVE"
        rigid_body.collision_shape = collision_shape
        rigid_body.collision_margin = collision_margin
        rigid_body.use_margin = True
        rigid_body.mesh_source = collision_mesh_source
        rigid_body.friction = friction
        rigid_body.angular_damping = angular_damping
        rigid_body.linear_damping = linear_damping

        if mass is None:
            rigid_body.mass = self.get_bound_box_volume() * mass_factor
        else:
            rigid_body.mass = mass

    def build_convex_decomposition_collision_shape(self, temp_dir, cache_dir="resources/decomposition_cache"):
        """ Builds a collision shape of the object by decomposing it into near convex parts using V-HACD

        :param temp_dir: The temp dir to use for storing the object files created by v-hacd.
        :param cache_dir: If a directory is given, convex decompositions are stored there named after the meshes hash. If the same mesh is decomposed a second time, the result is loaded from the cache and the actual decomposition is skipped.
        """
        # Decompose the object
        parts = convex_decomposition(self.blender_obj, temp_dir, cache_dir=Utility.resolve_path(cache_dir))
        parts = [MeshObject(p) for p in parts]

        # Make the convex parts children of this object, enable their rigid body component and hide them
        for part in parts:
            part.set_parent(self)
            part.enable_rigidbody(True, "CONVEX_HULL")
            part.hide()

    def hide(self, hide_object: bool = True):
        """ Sets the visibility of the object.

        :param hide_object: Determines whether the object should be hidden in rendering.
        """
        self.blender_obj.hide_render = hide_object

    def set_parent(self, new_parent: "MeshObject"):
        """ Sets the parent of this object.

        :param new_parent: The new parent object.
        """
        self.blender_obj.parent = new_parent.blender_obj
        self.blender_obj.matrix_parent_inverse = new_parent.blender_obj.matrix_world.inverted()

    def get_parent(self) -> "MeshObject":
        """ Returns the parent object.

        :return: The parent object, None if it has no parent.
        """
        return MeshObject(self.blender_obj.parent) if self.blender_obj.parent is not None else None

    def disable_rigidbody(self):
        """ Disables the rigidbody element of the object """
        bpy.ops.rigidbody.object_remove({'object': self.blender_obj})

    def get_rigidbody(self) -> bpy.types.RigidBodyObject:
        """ Returns the rigid body component

        :return: The rigid body component of the object.
        """
        return self.blender_obj.rigid_body

    def get_bound_box_volume(self) -> float:
        """ Gets the volume of the object aligned bounding box.

        :return: volume of a bounding box.
        """
        bb = self.get_bound_box()
        # Search for the point which is the maximum distance away from the first point
        # we call this first point min and the furthest away point max
        # the vector between the two is a diagonal of the bounding box
        min_point, max_point = bb[0], None
        max_dist = -1
        for point in bb:
            dist = np.linalg.norm(point - min_point)
            if dist > max_dist:
                max_point = point
                max_dist = dist
        diag = max_point - min_point
        # use the diagonal to calculate the volume of the box
        return abs(diag[0]) * abs(diag[1]) * abs(diag[2])

    def mesh_as_bmesh(self, return_copy=False) -> bmesh.types.BMesh:
        """ Returns a bmesh based on the object's mesh.

        Independent of return_copy, changes to the returned bmesh only take into affect after calling update_from_bmesh().

        :param return_copy: If True, a copy of the objects bmesh will be returned, otherwise the bmesh owned by blender is returned (the object has to be in edit mode for that).
        :return: The bmesh
        """
        if return_copy:
            bm = bmesh.new()
            bm.from_mesh(self.get_mesh())
        else:
            if bpy.context.mode != "EDIT_MESH":
                raise Exception(f"The object: {self.get_name()} is not in EDIT mode before calling mesh_as_bmesh()")
            bm = bmesh.from_edit_mesh(self.get_mesh())
        return bm

    def update_from_bmesh(self, bm: bmesh.types.BMesh, free_bm_mesh=True) -> bmesh.types.BMesh:
        """ Updates the object's mesh based on the given bmesh.

        :param bm: The bmesh to set.
        :param free_bm_mesh: If True and the given bmesh is not owned by blender, it will be deleted in the end.
        """
        # If the bmesh is owned by blender
        if bm.is_wrapped:
            # Just tell the mesh to update itself based on its bmesh
            bmesh.update_edit_mesh(self.get_mesh())
        else:
            # Set mesh from bmesh
            bm.to_mesh(self.get_mesh())
            # Optional: Free the bmesh
            if free_bm_mesh:
                bm.free()
        # Make sure the mesh is updated
        self.get_mesh().update()

    def edit_mode(self):
        """ Switch into edit mode of this mesh object """
        # Make sure we are in object mode
        if bpy.context.mode != "OBJECT":
            self.object_mode()

        # Set object active (Context overriding does not work for bpy.ops.object.mode_set)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = self.blender_obj
        self.blender_obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')

    def object_mode(self):
        """ Switch back into object mode """
        bpy.ops.object.mode_set(mode='OBJECT')

    def create_bvh_tree(self) -> mathutils.bvhtree.BVHTree:
        """ Builds a bvh tree based on the object's mesh.

        :return: The new bvh tree
        """
        bm = bmesh.new()
        bm.from_mesh(self.get_mesh())
        bm.transform(Matrix(self.get_local2world_mat()))
        bvh_tree = mathutils.bvhtree.BVHTree.FromBMesh(bm)
        bm.free()
        return bvh_tree

    @staticmethod
    def create_bvh_tree_multi_objects(mesh_objects: List["MeshObject"]) -> mathutils.bvhtree.BVHTree:
        """ Creates a bvh tree which contains multiple mesh objects.

        Such a tree is later used for fast raycasting.

        :param mesh_objects: The list of mesh objects that should be put into the BVH tree.
        :return: The built BVH tree.
        """
        # Create bmesh which will contain the meshes of all objects
        bm = bmesh.new()
        # Go through all mesh objects
        for obj in mesh_objects:
            # Add object mesh to bmesh (the newly added vertices will be automatically selected)
            bm.from_mesh(obj.get_mesh())
            # Apply world matrix to all selected vertices
            bm.transform(Matrix(obj.get_local2world_mat()), filter={"SELECT"})
            # Deselect all vertices
            for v in bm.verts:
                v.select = False

        # Create tree from bmesh
        bvh_tree = mathutils.bvhtree.BVHTree.FromBMesh(bm)
        bm.free()
        return bvh_tree

    @staticmethod
    def compute_poi(objects: List["MeshObject"]) -> np.ndarray:
        """ Computes a point of interest in the scene. Point is defined as a location of the one of the selected objects
        that is the closest one to the mean location of the bboxes of the selected objects.

        :param objects: The list of mesh objects that should be considered.
        :return: Point of interest in the scene.
        """
        # Init matrix for all points of all bounding boxes
        mean_bb_points = []

        for obj in objects:
            # Get bounding box corners
            bb_points = obj.get_bound_box()
            # Compute mean coords of bounding box
            mean_bb_points.append(np.mean(bb_points, axis=0))
        # Query point - mean of means
        mean_bb_point = np.mean(mean_bb_points, axis=0)
        # Closest point (from means) to query point (mean of means)
        poi = mean_bb_points[np.argmin(np.linalg.norm(mean_bb_points - mean_bb_point, axis=1))]

        return poi

    def position_is_above_object(self, position: Union[Vector, np.ndarray]):
        """ Make sure the given position is straight above the given object with no obstacles in between.

        :param position: The position to check.
        :return: True, if a ray sent into negative z-direction starting from the position hits the object first.
        """
        # Send a ray straight down and check if the first hit object is the query object
        hit, _, _, _, hit_object, _ = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph,
                                                                 Vector(position),
                                                                 Vector([0, 0, -1]))
        return hit and hit_object == self.blender_obj

    def ray_cast(self, origin: Union[Vector, list, np.ndarray], direction: Union[Vector, list, np.ndarray], max_distance: float = 1.70141e+38) -> Tuple[bool, np.ndarray, np.ndarray, int]:
        """ Cast a ray onto evaluated geometry, in object space.

        :param origin: Origin of the ray, in object space.
        :param direction: Direction of the ray, in object space.
        :param max_distance: Maximum distance.
        :return: Whether the ray successfully hit the geometry
                 The hit location of this ray cast, float array of 3 items in [-inf, inf]
                 The face normal at the ray cast hit location, float array of 3 items in [-inf, inf]
                 The face index, -1 when original data isn’t available, int in [-inf, inf]
        """
        result, location, normal, index = self.blender_obj.ray_cast(Vector(origin), Vector(direction), max_distance)
        return (result, np.array(location), np.array(normal), index)