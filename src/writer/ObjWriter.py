import bpy
from src.main.Module import Module

class ObjWriter(Module):

    def __init__(self, config):
        Module.__init__(self, config)

    def run(self):
        blend_path = self.config.get_string("path")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
