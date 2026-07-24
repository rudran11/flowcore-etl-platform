from flowcore_shared.plugins.models import PluginMetadata
from flowcore_server.models.plugin import PluginResponse

def map_plugin_to_response(plugin: PluginMetadata) -> PluginResponse:
    """
    Maps an internal Engine PluginMetadata model to a public API PluginResponse DTO.
    """
    return PluginResponse(
        plugin_id=plugin.plugin_id,
        name=plugin.name,
        version=plugin.version,
        plugin_type=plugin.plugin_type.value,
        author=plugin.author,
        description=plugin.description,
        category=plugin.category,
        capabilities=plugin.capabilities,
        supported_operations=plugin.supported_operations,
        example_yaml=plugin.example_yaml,
        documentation=plugin.documentation,
        compatibility=plugin.compatibility,
        dependencies=plugin.dependencies
    )
