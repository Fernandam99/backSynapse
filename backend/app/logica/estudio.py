#!/usr/bin/env python3
"""
Técnicas de Estudio con Cronómetro
Implementación de Pomodoro, 52-17, Ultradian y otras técnicas
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class StudyTimer:
    """Clase para manejar las técnicas de estudio con cronómetro"""
    
    def __init__(self):
        self.techniques = {
            'pomodoro': {
                'name': 'Técnica Pomodoro Clásica',
                'work': 25,  # minutos
                'break': 5,  # minutos
                'long_break': 30,  # después de 4 ciclos
                'cycles_for_long_break': 4,
                'description': '25min concentrado + 5min descanso. Descanso largo cada 4 ciclos.'
            },
            'study_52_17': {
                'name': 'Técnica 52-17',
                'work': 52,
                'break': 17,
                'long_break': 17,
                'cycles_for_long_break': 1,
                'description': '52min trabajo intenso + 17min descanso completo.'
            },
            'ultradian': {
                'name': 'Técnica Ultradian',
                'work': 90,
                'break': 20,
                'long_break': 20,
                'cycles_for_long_break': 1,
                'description': '90min siguiendo ritmos naturales + 20min descanso.'
            },
            'timeboxing': {
                'name': 'Timeboxing',
                'work': 45,
                'break': 15,
                'long_break': 30,
                'cycles_for_long_break': 3,
                'description': '45min por materia específica + 15min descanso.'
            },
            'study_45_15': {
                'name': 'Técnica 45-15',
                'work': 45,
                'break': 15,
                'long_break': 30,
                'cycles_for_long_break': 3,
                'description': '45min concentrado + 15min descanso activo.'
            },
            'intervals_15_5': {
                'name': 'Intervalos Cortos (15-5)',
                'work': 15,
                'break': 5,
                'long_break': 20,
                'cycles_for_long_break': 6,
                'description': '15min intenso + 5min pausa. Para temas difíciles.'
            },
            'flowtime': {
                'name': 'Flowtime',
                'work': 60,  # tiempo base, pero es flexible
                'break': 10,
                'long_break': 25,
                'cycles_for_long_break': 4,
                'description': 'Trabajo sin interrupciones forzadas, descansos naturales.',
                'flexible': True
            }
        }
        
        # Estado actual del temporizador
        self.current_technique = None
        self.current_phase = 'work'  # 'work', 'break', 'long_break'
        self.remaining_time = 0  # en segundos
        self.cycle_count = 0
        self.is_active = False
        self.start_time = None
        self.total_work_time = 0
        self.session_history = []
    
    def get_available_techniques(self) -> Dict[str, Any]:
        """Retorna las técnicas disponibles"""
        return self.techniques
    
    def start_technique(self, technique_key: str) -> Dict[str, Any]:
        """Inicia una técnica específica"""
        if technique_key not in self.techniques:
            raise ValueError(f"Técnica '{technique_key}' no encontrada")
        
        self.current_technique = self.techniques[technique_key]
        self.current_phase = 'work'
        self.remaining_time = self.current_technique['work'] * 60  # convertir a segundos
        self.cycle_count = 0
        self.is_active = True
        self.start_time = datetime.now()
        
        print(f"🚀 Iniciando: {self.current_technique['name']}")
        print(f"📝 {self.current_technique['description']}")
        
        return {
            'name': self.current_technique['name'],
            'work': self.current_technique['work'],
            'break': self.current_technique['break'],
            'phase': self.current_phase
        }
    
    def tick(self):
        """Reduce el tiempo en 1 segundo"""
        if self.is_active and self.remaining_time > 0:
            self.remaining_time -= 1
            
            # Si es Flowtime, permite extensión natural
            if (self.current_technique.get('flexible') and 
                self.current_phase == 'work' and 
                self.remaining_time == 0):
                self.handle_flowtime_completion()
    
    def handle_flowtime_completion(self):
        """Maneja la finalización flexible del Flowtime"""
        print("\n⏰ Tiempo base completado.")
        print("🌊 Flowtime: ¿Quieres continuar o tomar un descanso?")
        print("1. Continuar 15min más")
        print("2. Tomar descanso ahora")
        
        # En implementación real, esto esperaría input del usuario
        # Por ahora, simularemos continuar
        choice = "2"  # Simular elección de descanso
        
        if choice == "1":
            self.remaining_time = 15 * 60  # 15 minutos más
            print("➕ Extendiendo sesión por 15 minutos más")
        else:
            self.next_phase()
    
    def next_phase(self):
        """Cambia a la siguiente fase (trabajo -> descanso -> trabajo)"""
        if not self.is_active:
            return False
        
        if self.current_phase == 'work':
            self.total_work_time += self.current_technique['work']
            self.cycle_count += 1
            
            # Determinar tipo de descanso
            if (self.cycle_count % self.current_technique['cycles_for_long_break'] == 0):
                self.current_phase = 'long_break'
                self.remaining_time = self.current_technique['long_break'] * 60
                print(f"☕ Descanso largo: {self.current_technique['long_break']} minutos")
            else:
                self.current_phase = 'break'
                self.remaining_time = self.current_technique['break'] * 60
                print(f"⏸️ Descanso: {self.current_technique['break']} minutos")
                
        elif self.current_phase in ['break', 'long_break']:
            self.current_phase = 'work'
            self.remaining_time = self.current_technique['work'] * 60
            print(f"🔥 Trabajo: {self.current_technique['work']} minutos")
        
        return True
    
    def has_next_phase(self) -> bool:
        """Verifica si hay una siguiente fase"""
        return self.is_active
    
    def get_current_phase(self) -> str:
        """Retorna la fase actual"""
        return self.current_phase
    
    def get_next_phase(self) -> str:
        """Retorna el nombre de la siguiente fase"""
        if self.current_phase == 'work':
            if (self.cycle_count + 1) % self.current_technique['cycles_for_long_break'] == 0:
                return 'descanso largo'
            return 'descanso'
        return 'trabajo'
    
    def get_remaining_time(self) -> int:
        """Retorna el tiempo restante en segundos"""
        return max(0, self.remaining_time)
    
    def pause(self):
        """Pausa el temporizador"""
        self.is_active = False
        print("⏸️ Temporizador pausado")
    
    def resume(self):
        """Reanuda el temporizador"""
        self.is_active = True
        print("▶️ Temporizador reanudado")
    
    def reset(self):
        """Reinicia el temporizador"""
        if self.current_technique:
            self.current_phase = 'work'
            self.remaining_time = self.current_technique['work'] * 60
            self.cycle_count = 0
            self.is_active = True
            print("🔄 Temporizador reiniciado")
    
    def stop(self):
        """Detiene completamente el temporizador"""
        self.is_active = False
        self.current_technique = None
        self.current_phase = 'work'
        self.remaining_time = 0
        print("⏹️ Temporizador detenido")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de la sesión actual"""
        if not self.start_time:
            return {}
        
        elapsed = datetime.now() - self.start_time
        return {
            'technique': self.current_technique['name'] if self.current_technique else None,
            'elapsed_minutes': int(elapsed.total_seconds() / 60),
            'cycles_completed': self.cycle_count,
            'total_work_minutes': self.total_work_time,
            'current_phase': self.current_phase,
            'remaining_seconds': self.remaining_time
        }
    
    def add_custom_technique(self, work_minutes: int, break_minutes: int, name: str = None):
        """Añade una técnica personalizada"""
        if not name:
            name = f"Personalizada {work_minutes}-{break_minutes}"
        
        technique_key = f"custom_{len(self.techniques)}"
        self.techniques[technique_key] = {
            'name': name,
            'work': work_minutes,
            'break': break_minutes,
            'long_break': break_minutes * 2,
            'cycles_for_long_break': 4,
            'description': f'Técnica personalizada: {work_minutes}min trabajo + {break_minutes}min descanso.'
        }
        
        print(f"✅ Técnica '{name}' añadida exitosamente")
        return technique_key
    
    def get_productivity_tips(self, phase: str) -> str:
        """Retorna consejos de productividad según la fase"""
        tips = {
            'work': [
                "🎯 Elimina distracciones: silencia notificaciones",
                "📱 Coloca el teléfono en otra habitación",
                "🎵 Usa música instrumental o sonidos blancos",
                "💧 Ten agua cerca para mantenerte hidratado",
                "📝 Define una tarea específica antes de comenzar",
                "🪟 Asegúrate de tener buena iluminación",
                "🧘 Respira profundo y enfócate en el presente"
            ],
            'break': [
                "🚶 Levántate y camina unos minutos",
                "💧 Bebe agua para mantenerte hidratado",
                "👀 Mira algo lejano para relajar la vista",
                "🤸 Haz estiramientos simples",
                "🌱 Sal al aire libre si es posible",
                "🧘 Practica respiración profunda",
                "🚫 Evita redes sociales y pantallas"
            ],
            'long_break': [
                "🍎 Come algo saludable",
                "🚿 Considera una ducha rápida para refrescarte",
                "🧘 Practica meditación o mindfulness",
                "📞 Conecta con un amigo o familiar",
                "🌳 Sal a dar una caminata",
                "🎵 Escucha música relajante",
                "📚 Lee algo no relacionado con el estudio"
            ]
        }
        
        import random
        return random.choice(tips.get(phase, tips['work']))
    
    def save_session_to_history(self):
        """Guarda la sesión actual al historial"""
        if self.start_time and self.current_technique:
            session_data = {
                'date': datetime.now().isoformat(),
                'technique': self.current_technique['name'],
                'duration_minutes': int((datetime.now() - self.start_time).total_seconds() / 60),
                'cycles_completed': self.cycle_count,
                'work_minutes': self.total_work_time
            }
            self.session_history.append(session_data)
            print(f"💾 Sesión guardada en historial")
    
    def get_weekly_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas semanales"""
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        recent_sessions = [
            session for session in self.session_history
            if datetime.fromisoformat(session['date']) >= week_ago
        ]
        
        if not recent_sessions:
            return {'sessions': 0, 'total_minutes': 0, 'average_session': 0}
        
        total_minutes = sum(session['work_minutes'] for session in recent_sessions)
        
        return {
            'sessions': len(recent_sessions),
            'total_minutes': total_minutes,
            'average_session': total_minutes // len(recent_sessions) if recent_sessions else 0,
            'most_used_technique': self._get_most_used_technique(recent_sessions)
        }
    
    def _get_most_used_technique(self, sessions) -> str:
        """Determina la técnica más utilizada"""
        technique_counts = {}
        for session in sessions:
            technique = session['technique']
            technique_counts[technique] = technique_counts.get(technique, 0) + 1
        
        if not technique_counts:
            return "Ninguna"
        
        return max(technique_counts, key=technique_counts.get)