import pluggy

APP_NAME = "asset-manager"

hook_impl = pluggy.HookimplMarker(APP_NAME)
"""Storage providers can use this hook to implement custom storage class
"""

hook_spec = pluggy.HookspecMarker(APP_NAME)
"""hook_spec is used to standardize the calling within asset-core and registering and discovering plugins
"""
