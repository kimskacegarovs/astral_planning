const planning_request = {transport_id: null, shipment_id: null}
let currentTarget = null;

const getType = (item) => item.getAttribute("data-item-type")
const isSameType = (item1, item2) => getType(item1) === getType(item2)
const isTransport = (item) => getType(item) === "transport"
const isShipment = (item) => getType(item) === "shipment"

function connectRows(item1, item2) {
    if (isSameType(item1, item2)) return

    if (isTransport(item1) && isShipment(item2)) {
        planning_request.transport_id = item1.id
        planning_request.shipment_id = item2.id
    } else if (isTransport(item2) && isShipment(item1)) {
        planning_request.transport_id = item2.id
        planning_request.shipment_id = item1.id
    }

    document.getElementById('planning-form').click()
}

function highlightRow(row) {
    row.classList.remove('bg-gray-700');
    row.classList.add('bg-gray-600', 'transition', 'duration-500');
}

function dimRow(row) {
    row.classList.remove('bg-gray-600');
    row.classList.add('bg-gray-700', 'transition', 'duration-500');
}

function applyDraggable() {
    document.querySelectorAll('.draggable').forEach(item => {
        item.addEventListener('mouseover', event => {
            highlightRow(event.target);
        });

        item.addEventListener('mouseout', event => {
            dimRow(event.target);
        });

        item.addEventListener('dragstart', event => {
            event.dataTransfer.setData('text/plain', event.target.id);
            highlightRow(event.target);
            currentTarget = event.target;
        });

        item.addEventListener('dragend', event => {
            event.dataTransfer.clearData();
            dimRow(event.target);
            currentTarget = null;
        });

        item.addEventListener('dragenter', event => {
            highlightRow(event.target);
        });

        item.addEventListener('dragleave', event => {
            if (event.target !== currentTarget) {
                dimRow(event.target);
            }
        });

        item.addEventListener('dragover', event => {
            event.preventDefault();
        });

        item.addEventListener('drop', event => {
            event.preventDefault();
            dimRow(event.target);
            connectRows(currentTarget, event.target);
        });
    });
}
