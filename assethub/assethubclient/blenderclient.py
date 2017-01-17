import bpy

try:
    from sverchok.utils.sv_IO_panel_tools import import_tree
    SVERCHOK_AVAILABLE=True
except ImportError:
    SVERCHOK_AVAILABLE=False

from os.path import join, basename
import json

from assethubclient import client

class Asset(client.Asset):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], client.Asset) and not kwargs:
            self.dict = args[0].dict
        else:
            super(Asset, self).__init__(*args, **kwargs)

    def is_text(self):
        ctype = self.get_data_content_type()
        return ctype.startswith('text/') or (ctype == 'application/json')
    
    def is_json(self):
        ctype = self.get_data_content_type()
        return ctype == 'application/json'

    def get_json_data(self):
        result = self.get_data(content_type='application/json')
        return json.loads(result.decode('utf-8'))

    def store_to_text_block(self, name=None):
        if not self.is_text():
            raise TypeError("Asset content type is not text")
        
        if name is None:
            name = basename(self.data)

        if not name in bpy.data.texts:
            bpy.data.texts.new(name)

        content = self.get_data()
        bpy.data.texts[name].clear()
        bpy.data.texts[name].write(content.decode('utf-8'))

    def import_sverchok_tree(self, name=None):
        if not SVERCHOK_AVAILABLE:
            raise ImportError("Sverchok is not available")

        if not name:
            name = basename(self.data)
        json = self.get_json_data()
        ng = bpy.data.node_groups.new(name=name, type='SverchCustomTreeType')
        import_tree(ng, nodes_json=json)

class AssetHubClient(client.AssetHubClient):
    def __init__(self, *args, **kwargs):
        super(AssetHubClient, self).__init__(*args, **kwargs)
        self.asset_constructor = Asset
        if not self.application:
            self.application = 'blender'

    def post_text_block(self, name, license=None):
        if license is None:
            license = self.license
        if license is None:
            license = "CC0"
        content = bpy.data.texts[name].as_string()
        asset = Asset(dict(title=name, application=self.application, component=self.component, license=license))
        return self.post(asset, content)

