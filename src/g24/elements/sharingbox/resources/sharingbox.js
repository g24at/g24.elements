// TODO: wrapping in anonymous function?
// TODO: $ globally accessible, isn't it? how is mockup doing it?


function feature_toggle(el, scope, name) {
    // el .. (jQuery object) .. toggle button
    // scope .. (jQuery object) .. scope to find feature fieldset in
    // name .. (string) .. feature name, used as id on fieldset
    if (el.prop('checked')===true) {
        scope.find('fieldset#' + name).show();
    } else {
        scope.find('fieldset#' + name).hide();
    }
}


function init_feature_toggle() {
    var tmp_el;
    tmp_el = $('input#features-widgets-is_event-0');
    if (tmp_el.length>0) {
        feature_toggle(tmp_el, tmp_el.closest('form'), 'event');
        tmp_el = $('input#features-widgets-is_place-0');
        feature_toggle(tmp_el, tmp_el.closest('form'), 'place');

        $('input#features-widgets-is_event-0').change(function () {
            feature_toggle($(this), $(this).closest('form'), 'event');
        });

        $('input#features-widgets-is_place-0').change(function () {
            feature_toggle($(this), $(this).closest('form'), 'place');
        });
    }
}


function initialize_map() {
    // Initialize the map

    $('.geolocation_wrapper').each(function () {
        var $this = $(this);
        var $map = $('.geomap', $this);
        var $geocodes = $('.geolocation', $this);
        var editable = $this.hasClass('edit');
        var map = new L.Map($map, {});

        L.tileLayer.provider('OpenStreetMap.DE').addTo(map);
        var baseLayers = ['OpenStreetMap.DE', 'Esri.WorldImagery', 'Esri.WorldStreetMap', 'OpenCycleMap'];
        var layerControl = L.control.layers.provided(baseLayers).addTo(map);

        var fullScreen = new L.Control.FullScreen();
        map.addControl(fullScreen);

        // ADD MARKERS
        var markers = new L.MarkerClusterGroup();
        $geocodes.each(function() {
            var geo = $(this).data();
            var marker = new L.Marker([geo.latitude, geo.longitude],
                                      {draggable: editable});
            marker.bindPopup(geo.description);
            if (editable) {
                marker.on('dragend', function (e) {
                    var coords = e.target.getLatLng();
                    update_inputs(coords.lat, coords.lng);
                });
            }
            markers.addLayer(marker);
        });
        map.addLayer(markers);

        // autozoom
        var bounds = markers.getBounds();
        map.fitBounds(bounds);

        if (editable) {
            var update_inputs = function(lat, lng) {
                $('input.latitude', $this).attr('value', lat);
                $('input.longitude', $this).attr('value', lng);
            };
            map.on('geosearch_showlocation', function (e) {
                var coords = e.Location;
                update_inputs(coords.Y, coords.X);
            });

            // GEOSEARCH
            var geosearch = new L.Control.GeoSearch({
                draggable: editable,
                provider: new L.GeoSearch.Provider.Google()
                //provider: new L.GeoSearch.Provider.OpenStreetMap()
            }).addTo(map);
        }

    });

}



$(document).bind("ajaxComplete", function(){
    // bind to sharingbox loaded via ajax
    // TODO: bind tighter to shbx call - otherwise this is called with every
    // ajax request
    init_feature_toggle();
    initialize_map();
});

$(document).ready(function() {

    initialize_map();

    /*
    var features = ["event", "place"];
    var i;
    for (i = 0; i < features.length; i++) {
        var feature = features[i];
        var input = $('input#features-widgets-is_' + feature + '-0');
        input.change(function () {
            feature_toggle(input, input.closest('form'), feature);
        });
        feature_toggle(input, input.closest('form'), feature);
    }
    */

});
