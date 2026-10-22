"""
Regresión: un DELETE no debe hacer que la siguiente reserva repita un ID.

Antes, POST /add_reservation asignaba len(reservations) + 1. Con A y B creadas
y A borrada, la nueva reserva C recibía el mismo ID que B; luego un DELETE por
ese ID borraba una de las dos y un segundo DELETE devolvía 200 en vez de 404.
"""

import pytest

from gestionreservas_common import (
    delete_reservas,
    find_route_and_free_seat,
    make_add_reservation_body,
    post_reservas,
)


def _create_reservation() -> dict:
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
    return r.json()["reservation"]


def test_reservation_id_is_not_reused_after_delete():
    a = _create_reservation()
    b = _create_reservation()

    r = delete_reservas(f"/delete_reservation_by_id/{a['reservation_id']}")
    assert r.status_code == 200, f"{r.status_code} {r.text}"

    c = _create_reservation()
    try:
        assert c["reservation_id"] != b["reservation_id"], (
            f"La reserva nueva reutilizó el ID {b['reservation_id']} de una reserva existente"
        )
    finally:
        for res in (b, c):
            delete_reservas(f"/delete_reservation_by_id/{res['reservation_id']}")
