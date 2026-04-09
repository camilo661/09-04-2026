# 🚖 TaxisDrive — Pasto

Sistema de pedidos de transporte público para la ciudad de Pasto, Nariño.
Implementado con **Listas Doblemente Enlazadas** como estructura de datos principal.

---

## 📁 Estructura del Proyecto

```
taxisdrive/
├── app.py                        # Flask app principal (rutas API + Frontend)
├── requirements.txt
├── backend/
│   ├── __init__.py
│   ├── node.py                   # Nodo de la lista doblemente enlazada
│   ├── doubly_linked_list.py     # Implementación de la lista doble
│   ├── vehicle.py                # Modelo de vehículo
│   ├── order.py                  # Modelo de pedido
│   ├── fleet_manager.py          # Gestión de flota (10 vehículos / Pasto)
│   └── order_manager.py          # Gestión de pedidos
└── frontend/
    ├── templates/
    │   └── index.html            # SPA principal
    └── static/
        ├── css/style.css         # Estilos (diseño urbano oscuro)
        └── js/app.js             # Lógica del frontend
```

---

## 🚀 Instalación y Ejecución

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar el servidor
```bash
python app.py
```

### 3. Abrir en el navegador
```
http://localhost:5000
```

---

## 🏗️ Estructura de Datos: Lista Doblemente Enlazada

La flota de vehículos está almacenada en una `DoublyLinkedList`:

- Cada nodo (`Node`) contiene un objeto `Vehicle` + punteros `next` y `prev`
- El primer nodo = **cabeza** (`head`), el último = **cola** (`tail`)
- Soporte de recorrido en **ambas direcciones**
- Operaciones: `append`, `prepend`, `insert`, `remove`, `find_nearest_available`

### Algoritmo de búsqueda de vehículo más cercano
1. El usuario ingresa su **barrio** → sistema detecta el **sector** en Pasto
2. Se recorre la lista doble buscando vehículos `disponible`
3. Se calcula distancia Euclidiana entre vehículo y sector destino
4. Los vehículos del **mismo sector** reciben un **bonus de proximidad** (×0.5)
5. Se asigna el vehículo con menor distancia ajustada

---

## 🗺️ Sectores de Pasto simulados

| Sector | Descripción |
|--------|-------------|
| Centro | Centro Histórico, Plaza de Nariño |
| Lorenzo | San Lorenzo, El Tejar |
| Torobajo | Torobajo, La Estrella |
| Chambú | Chambú, Los Pinos |
| Corazón de Jesús | Corazón de Jesús, El Calvario |
| San Ignacio | San Ignacio, La Merced |
| Aranda | Aranda, Villa Lucía |
| La Minga | La Minga, El Lago |
| Jamondino | Jamondino, San Martin |
| Riveras de Mijitayo | Riveras de Mijitayo, El Mirador |

---

## 📡 API REST

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/fleet` | Todos los vehículos + estadísticas |
| GET | `/api/sectors` | Sectores y barrios de Pasto |
| POST | `/api/orders` | Crear nuevo pedido |
| GET | `/api/orders` | Todos los pedidos |
| PUT | `/api/orders/:id/complete` | Completar pedido |
| PUT | `/api/orders/:id/cancel` | Cancelar pedido |

---

## 👨‍💻 Tecnologías

- **Backend:** Python 3.11 · Flask · OOP pura
- **Estructura de datos:** Lista Doblemente Enlazada (implementación manual)
- **Frontend:** HTML5 · CSS3 · JavaScript ES6+ (sin frameworks)
- **Fuente:** Syne + DM Sans (Google Fonts)

---

*Proyecto académico — Estructuras de Datos · Universidad Cooperativa de Colombia · Pasto 2026*
