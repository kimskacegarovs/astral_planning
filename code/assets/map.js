function getConvertedCoordinates(coordinatesRaw) {
    return coordinatesRaw.map(coordStr => {
        const cleanedStr = coordStr.replace(/[()]/g, '');
        const [latitude, longitude] = cleanedStr.split(',').map(coord => parseFloat(coord.trim()));
        return [latitude, longitude];
    });
}

function removeExistingMapLayers() {
    mymap.eachLayer(function (layer) {
        if (layer instanceof L.Marker || layer instanceof L.Polyline) {
            mymap.removeLayer(layer);
        }
    });
}

var mapMarkerEmojis = {
    plannedTransport: '🚚',
    plannedShipment: '🎁',
    transport: '🚛',
    shipment: '📦',
}

function getEmojiIcon(emoji) {
    return L.divIcon({
        html: emoji,
        iconSize: [40, 40],
        iconAnchor: [12, 24],
        className: 'transparent-marker'
    });
}

var mapMaprkerIcons = {
    plannedTransport: getEmojiIcon(mapMarkerEmojis.plannedTransport),
    plannedShipment: getEmojiIcon(mapMarkerEmojis.plannedShipment),
    transport: getEmojiIcon(mapMarkerEmojis.transport),
    shipment: getEmojiIcon(mapMarkerEmojis.shipment),
}

function addMapMarkerPopup(rawCoordinates, markerEmoji) {
    const coordinatesArray = getConvertedCoordinates(rawCoordinates)
    coordinatesArray.forEach(function (coord) {
        L.marker(coord, {icon: markerEmoji}).addTo(mymap);
    });
}

function addMapLines(rawCoordinates) {
    const defaultColor = '#3388ff';
    rawCoordinates.forEach(function (coord) {
        const randomColor = getRandomColor();
        const path = L.polyline.antPath(coord, {
            "delay": 600,
            "dashArray": [10, 20],
            "weight": 5,
            "color": randomColor,
            "pulseColor": "#FFFFFF",
            "paused": false,
            "reverse": false,
            "hardwareAccelerated": true
        });
        mymap.addLayer(path);
    });
}

function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        const randomIndex = i === 0 ? Math.floor(Math.random() * 10) : Math.floor(Math.random() * 7);
        color += letters[randomIndex];
    }
    return color;
}

const mapContainerId = 'mapid';
let mymap = undefined;

function initMap() {
    mymap = L.map(mapContainerId).setView(centerCoordinate, mapZoom);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(mymap);

    return mymap;
}

function setMap() {
    if (mymap !== undefined) mymap.remove();
    initMap();
    addMapMarkerPopup(coordinatesRawPlannedTransport, mapMaprkerIcons.plannedTransport)
    addMapMarkerPopup(coordinatesRawPlannedShipments, mapMaprkerIcons.plannedShipment)
    addMapMarkerPopup(coordinatesRawTransport, mapMaprkerIcons.transport)
    addMapMarkerPopup(coordinatesRawShipments, mapMaprkerIcons.shipment)
    addMapLines(plannedLines)
}
