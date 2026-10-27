#!/usr/bin/env python3
"""Demo de la TFU UT3. Solo usa la librería estándar.

Uso:  python scripts/demo.py [stateless|acid|concurrency|all]
      BASE_URL=http://localhost:8080 por defecto.
"""
import json
import os
import sys
import threading
import urllib.error
import urllib.request
import uuid
from collections import Counter

BASE = os.getenv("BASE_URL", "http://localhost:8080")


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or b"null"), r.headers
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null"), e.headers


def new_customer():
    _, c, _ = call("POST", "/customers",
                   {"name": "Cliente Demo", "email": f"{uuid.uuid4().hex[:8]}@demo.com"})
    return c["id"]


def new_product(name, price, stock):
    _, p, _ = call("POST", "/products", {"name": name, "price": price, "stock": stock})
    return p["id"]


def stock_of(product_id):
    return call("GET", f"/products/{product_id}")[1]["stock"]


def title(text):
    print(f"\n=== {text} ===")


def demo_stateless():
    title("Servicios sin estado + escalabilidad horizontal")
    print("20 requests a /health: ¿qué réplica atendió cada una?")
    hosts = Counter(call("GET", "/health")[1]["served_by"] for _ in range(20))
    for host, n in sorted(hosts.items()):
        print(f"  contenedor {host}: {n} requests")
    print(f"Réplicas distintas observadas: {len(hosts)}")


def demo_acid():
    title("ACID: atomicidad (todo o nada)")
    cust = new_customer()
    a = new_product("Producto A", "10.00", 5)
    b = new_product("Producto B", "20.00", 1)
    print(f"Stock inicial -> A: {stock_of(a)}, B: {stock_of(b)}")
    print("Orden con 2 de A (hay stock) y 5 de B (NO hay stock)...")
    status, body, _ = call("POST", "/orders", {
        "customer_id": cust,
        "items": [{"product_id": a, "quantity": 2}, {"product_id": b, "quantity": 5}],
    })
    print(f"Respuesta: {status} {body}")
    print(f"Stock final   -> A: {stock_of(a)}, B: {stock_of(b)}")
    ok = status == 409 and stock_of(a) == 5 and stock_of(b) == 1
    print("RESULTADO:", "OK, rollback completo (A sigue en 5)" if ok else "FALLÓ, revisar")


def demo_concurrency():
    title("ACID: aislamiento (concurrencia sobre el mismo producto)")
    cust = new_customer()
    prod = new_product("Producto escaso", "15.00", 10)
    n_requests = 30
    print(f"Stock inicial: 10. Lanzando {n_requests} órdenes simultáneas de 1 unidad...")
    results, lock = [], threading.Lock()

    def worker():
        status, _, _ = call("POST", "/orders", {
            "customer_id": cust, "items": [{"product_id": prod, "quantity": 1}]})
        with lock:
            results.append(status)

    threads = [threading.Thread(target=worker) for _ in range(n_requests)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    counts = Counter(results)
    final = stock_of(prod)
    print(f"Respuestas: {dict(counts)}  |  Stock final: {final}")
    ok = counts.get(201) == 10 and counts.get(409) == n_requests - 10 and final == 0
    print("RESULTADO:", "OK, exactamente 10 vendidas, sin sobreventa" if ok else "FALLÓ, revisar")


COMMANDS = {"stateless": demo_stateless, "acid": demo_acid, "concurrency": demo_concurrency}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which == "all":
        for fn in COMMANDS.values():
            fn()
    elif which in COMMANDS:
        COMMANDS[which]()
    else:
        sys.exit(f"Opciones: {', '.join(COMMANDS)}, all")
