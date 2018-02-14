import os
import requests

from routes import url_for

import ckan.plugins as p
from ckan.tests import helpers, factories
from ckan.common import config

from ckanext.geoview.plugin import (
    get_proxified_service_url,
    get_common_map_config,
    load_basemaps,
    get_openlayers_viewer_config
)


class TestPlugin(helpers.FunctionalTestBase):

    @classmethod
    def setup_class(self):

        super(TestPlugin, self).setup_class()

        if not p.plugin_loaded('geo_view'):
            p.load('geo_view')

        if not p.plugin_loaded('geojson_view'):
            p.load('geojson_view')

        if not p.plugin_loaded('wmts_view'):
            p.load('wmts_view')

        self.app = self._get_test_app()

    @classmethod
    def teardown_class(self):
        p.unload('geo_view')
        p.unload('geojson_view')
        p.unload('wmts_view')

        super(TestPlugin, self).teardown_class()

        helpers.reset_db()

    def test_get_proxified_service_url(self):
        dataset = factories.Dataset()
        resource = factories.Resource()

        proxified_url = get_proxified_service_url({
            'package': dataset,
            'resource': resource
        })

        assert proxified_url == \
            '/dataset/{0}/resource/{1}/service_proxy'.format(
                dataset.get('name'),
                resource.get('id')
            )

    @helpers.change_config('ckanext.spatial.common_map.type', 'mapbox')
    @helpers.change_config('ckanext.spatial.common_map.map_id', '123')
    @helpers.change_config('ckanext.spatial.common_map.access_token', '456')
    def test_get_common_map_config(self):
        map_config = get_common_map_config()

        assert map_config.get('type') == 'mapbox'
        assert map_config.get('map_id') == '123'
        assert map_config.get('access_token') == '456'

    def test_load_basemaps(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        basemaps_config = load_basemaps(dir_path + '/basemaps.json')

        assert len(basemaps_config) == 2
        assert basemaps_config[0].get('title') == 'OSM'
        assert basemaps_config[1].get('title') == 'Opengeo WMS demo'

    @helpers.change_config('ckanext.geoview.ol_viewer.formats', 'wms kml')
    @helpers.change_config('ckanext.geoview.ol_viewer.hide_overlays', True)
    def test_get_openlayers_viewer_config(self):
        openlayers_config = get_openlayers_viewer_config()

        assert openlayers_config.get('formats') == 'wms kml'
        assert openlayers_config.get('hide_overlays') is True

    def test_create_geo_view(self):
        resource = factories.Resource()

        resource_view = factories.ResourceView(
            resource_id=resource['id'],
            view_type='geo_view',
            feature_hoveron=True,
            feature_style='some style')

        assert resource_view.get('view_type') == 'geo_view'
        assert resource_view.get('feature_hoveron') is True
        assert resource_view.get('feature_style') == 'some style'

    def test_create_geojson_view(self):
        resource = factories.Resource()

        resource_view = factories.ResourceView(
            resource_id=resource['id'],
            view_type='geojson_view')

        assert resource_view.get('view_type') == 'geojson_view'

    def test_create_wmts_view(self):
        resource = factories.Resource()

        resource_view = factories.ResourceView(
            resource_id=resource['id'],
            view_type='wmts_view')

        assert resource_view.get('view_type') == 'wmts_view'
