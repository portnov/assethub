import bpy
from bpy.types import WindowManager, AddonPreferences
from bpy.props import StringProperty, EnumProperty

try:
    from sverchok.utils.sv_IO_panel_tools import import_tree
    SVERCHOK_AVAILABLE=True
except ImportError:
    SVERCHOK_AVAILABLE=False

from os.path import join, basename, dirname, exists
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

assethub_client = None
assethub_components = []
preview_collections = {}

def get_assethub_client(context):
    global assethub_client

    if assethub_client is not None:
        return assethub_client
    addon = bpy.context.user_preferences.addons.get("assethubclient").preferences
    assethub_client = AssetHubClient(addon.assethub_url, application="blender")
    return assethub_client

def previews_from_assethub(self, context):

    enum_items = []
    if context is None:
        return enum_items

    wm = context.window_manager
    component = self.assethub_component
    if not component:
        return enum_items

    directory = join(dirname(__file__), "thumbs", component)
    pcoll = preview_collections.get(component, None)
    if pcoll is None:
        pcoll = bpy.utils.previews.new()
        pcoll.previews = []
        preview_collections[component] = pcoll
    if pcoll.previews:
        return pcoll.previews

    c = get_assethub_client(context)
    c.component = component
    for idx, asset in enumerate(c.list()):
        id = str(asset.id)
        if not asset.image:
            icon = 'NONE'
        else:
            thumbnail_path = join(directory, asset.get_thumbnail_name())
            if not exists(thumbnail_path):
                asset.download_thumbnail(thumbnail_path)
            if id not in pcoll:
                thumb = pcoll.load(id, thumbnail_path, 'IMAGE')
            else:
                thumb = pcoll[id]
            icon = thumb.icon_id
        if asset.notes:
            notes = asset.notes
        else:
            notes = asset.title
        enum_items.append((id, asset.title, notes, icon, idx))
    
    pcoll.previews = enum_items
    return enum_items

def components_from_assethub(self, context):
    global assethub_components
    #assethub_components = []

    if len(assethub_components) > 0 or context is None:
        return assethub_components

    c = get_assethub_client(context)
    for idx, comp in enumerate(c.get_components()):
        notes = comp.notes_en
        if not notes:
            notes = comp.title_en
        assethub_components.append((comp.slug, comp.title_en, notes))

    #print(assethub_components)
    return assethub_components

class ImportOperator(bpy.types.Operator):
    bl_label = "Import from AssetHub"
    bl_idname = "import.assethub"

    assethub_component = EnumProperty(items = components_from_assethub)
    asset = EnumProperty(items = previews_from_assethub)

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "assethub_component")

        row = layout.row()
        row.prop(self, "asset")
        #row = layout.row()
        #row.template_icon_view(self, "asset")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        print("Params: comp={}, preview={}".format(self.assethub_component, self.asset))
        c = get_assethub_client(context)
        asset = c.get(self.asset)
        if self.assethub_component == "sverchok-sn1":
            asset.store_to_text_block()
        elif self.assethub_component == "sverchok-layout":
            asset.import_sverchok_tree()
        return {'FINISHED'}

class SettingsPanel(bpy.types.AddonPreferences):
    bl_label = "AssetHub settings"
    bl_idname = __package__

    assethub_url = StringProperty(
        name = "AssetHub URL",
        default = "http://assethub.iportnov.tech/")

    def draw(self, context):
        layout = self.layout
        #wm = context.window_manager

        row = layout.row()
        row.prop(self, "assethub_url")

def menu_func(self, context):
    self.layout.operator("import.assethub", text="Import from AssetHub")

def register():


    bpy.utils.register_class(ImportOperator)
    bpy.utils.register_class(SettingsPanel)
    bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    from bpy.types import WindowManager

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    bpy.utils.unregister_class(ImportOperator)
    bpy.utils.unregister_class(SettingsPanel)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()

