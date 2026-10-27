# Mini e-commerce – UT3 TFU

API REST en Python (FastAPI) con módulos Products, Customers y Orders,
PostgreSQL (ACID), Nginx como gateway y Docker Compose.

## Levantar
    docker compose up --build --scale api=3

## Probar (http://localhost:8080, docs en /docs)
    python scripts/demo.py stateless     # reparto entre réplicas
    python scripts/demo.py acid          # rollback completo
    python scripts/demo.py concurrency   # sin sobreventa
    python scripts/demo.py all

## Con curl
    curl -X POST localhost:8080/customers -H "Content-Type: application/json" -d '{"name":"Ana","email":"ana@demo.com"}'
    curl -X POST localhost:8080/products  -H "Content-Type: application/json" -d '{"name":"Teclado","price":"25.00","stock":10}'
    curl -X POST localhost:8080/orders    -H "Content-Type: application/json" -d '{"customer_id":1,"items":[{"product_id":1,"quantity":2}]}'
    curl -i localhost:8080/health        # mirar X-Served-By

## Apagar
    docker compose down      # agregar -v para borrar los datos
