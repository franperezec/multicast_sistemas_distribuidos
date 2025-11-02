# -*- coding: utf-8 -*-
"""
Agregador de Estadísticas de Nodos
Lee los archivos de estadísticas de los nodos simulados y genera un reporte consolidado
"""

import os
import json
import time
from datetime import datetime
from collections import defaultdict


def aggregate_node_stats():
    """
    Lee y agrega las estadísticas de todos los nodos activos
    """
    stats = {
        'total_messages': 0,
        'total_bytes': 0,
        'nodes_seen': set(),
        'messages_per_node': defaultdict(int),
        'bytes_per_node': defaultdict(int),
        'message_types': defaultdict(int),
        'errors': 0
    }

    # Buscar archivos de estadísticas de nodos
    stats_dir = 'logs/node_stats'
    if not os.path.exists(stats_dir):
        return stats

    for filename in os.listdir(stats_dir):
        if filename.startswith('node_') and filename.endswith('_stats.json'):
            filepath = os.path.join(stats_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    node_stats = json.load(f)

                node_name = node_stats.get('node_name', 'Unknown')
                stats['nodes_seen'].add(node_name)

                # Agregar estadísticas
                msgs_sent = node_stats.get('messages_sent', 0)
                bytes_sent = node_stats.get('bytes_sent', 0)
                msgs_received = node_stats.get('messages_received', 0)
                bytes_received = node_stats.get('bytes_received', 0)

                stats['messages_per_node'][node_name] = msgs_sent + msgs_received
                stats['bytes_per_node'][node_name] = bytes_sent + bytes_received
                stats['total_messages'] += msgs_sent + msgs_received
                stats['total_bytes'] += bytes_sent + bytes_received
                stats['errors'] += node_stats.get('errors', 0)

            except Exception as e:
                print(f"Error leyendo {filename}: {e}")

    return stats


def generate_aggregate_report():
    """
    Genera un reporte consolidado de todos los nodos
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/aggregate_report_{timestamp}.txt"

    stats = aggregate_node_stats()

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("REPORTE AGREGADO DE NODOS MULTICAST\n")
            f.write(f"Fecha: {datetime.now()}\n")
            f.write("="*70 + "\n\n")

            # Información general
            f.write("ESTADÍSTICAS GENERALES\n")
            f.write("-"*30 + "\n")
            f.write(f"Total de mensajes: {stats['total_messages']}\n")
            f.write(f"Total de bytes: {stats['total_bytes']}\n")
            f.write(f"Nodos detectados: {len(stats['nodes_seen'])}\n")
            f.write(f"Errores: {stats['errors']}\n\n")

            # Actividad por nodo
            f.write("ACTIVIDAD POR NODO\n")
            f.write("-"*30 + "\n")
            for node, count in sorted(stats['messages_per_node'].items()):
                bytes_total = stats['bytes_per_node'][node]
                f.write(f"{node}: {count} mensajes, {bytes_total} bytes\n")

            f.write("\n" + "="*70 + "\n")

        print(f"✅ Reporte agregado guardado en: {filename}")
        return filename

    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
        return None


if __name__ == "__main__":
    # Generar reporte si se ejecuta directamente
    generate_aggregate_report()
