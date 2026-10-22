"""
Smoke test de GestiónReservas: crear una reserva válida y recuperarla por código.

Usa una ruta y un asiento Libre reales de GestiónVuelos, y borra la reserva al
final para no dejar el asiento ocupado.
"""

import pytest

from gestionreservas_common import (
    delete_reservas,
    find_route_and_free_seat,
    get_reservas,
    make_add_reservation_body,
    post_reservas,
)


def test_crear_reserva_contrato_y_estado():
    pair = find_route_and_free_seat()
    if pair is None:
        pytest.skip("No hay ninguna combinación (ruta, asiento Libre) en GestiónVuelos.")
    ruta, seat = pair

    body = make_add_reservation_body(
        airplane_id=ruta["airplane_id"],
        airplane_route_id=ruta["airplane_route_id"],
        seat_number=seat["seat_number"],
    )
    r = post_reservas("/add_reservation", json=body)
    assert r.status_code == 201, f"{r.status_code} {r.text}"

    reserva = r.json()["reservation"]
    assert reserva["status"] == "Reservado"
    assert reserva.get("reservation_code"), "Falta reservation_code en la respuesta"

    try:
        r2 = get_reservas(f"/get_reservation_by_code/{reserva['reservation_code']}")
        assert r2.status_code == 200, f"{r2.status_code} {r2.text}"
        assert r2.json()["reservation_id"] == reserva["reservation_id"]
    finally:
        delete_reservas(f"/delete_reservation_by_id/{reserva['reservation_id']}")
