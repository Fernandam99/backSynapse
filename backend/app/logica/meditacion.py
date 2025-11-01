#!/usr/bin/env python3
"""
Técnicas de Meditación y Respiración Pre-Estudio
Implementación de respiración 4-7-8, Box Breathing, Mindfulness
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import math

class MeditationTimer:
    """Clase para manejar las técnicas de meditación y respiración"""
    
    def __init__(self):
        self.techniques = {
            'breathing_4_7_8': {
                'name': 'Respiración 4-7-8 (Calmante)',
                'duration': 4,  # minutos totales
                'cycles': 4,
                'inhale': 4,    # segundos
                'hold': 7,      # segundos
                'exhale': 8,    # segundos
                'pause': 0,     # segundos
                'description': 'Inhala 4s, retén 7s, exhala 8s. Excelente para ansiedad.',
                'benefits': ['Reduce ansiedad', 'Calma el sistema nervioso', 'Mejora el sueño'],
                'instructions': [
                    'Siéntate cómodamente con la espalda recta',
                    'Coloca la lengua contra el paladar superior',
                    'Exhala completamente por la boca',
                    'Inhala por la nariz contando hasta 4',
                    'Retén la respiración contando hasta 7',
                    'Exhala por la boca contando hasta 8'
                ]
            },
            'box_breathing': {
                'name': 'Respiración Cuadrada (Box Breathing)',
                'duration': 8,
                'cycles': 8,
                'inhale': 4,
                'hold': 4,
                'exhale': 4,
                'pause': 4,
                'description': 'Inhala 4s, retén 4s, exhala 4s, pausa 4s. Para concentración.',
                'benefits': ['Mejora concentración', 'Reduce estrés', 'Aumenta claridad mental'],
                'instructions': [
                    'Busca una posición cómoda',
                    'Respira naturalmente unas veces',
                    'Inhala lentamente por 4 segundos',
                    'Mantén el aire por 4 segundos',
                    'Exhala suavemente por 4 segundos',
                    'Permanece vacío por 4 segundos'
                ]
            },
            'mindfulness_5': {
                'name': 'Atención Plena 5 minutos',
                'duration': 5,
                'cycles': 1,
                'inhale': 0,  # Respiración natural
                'hold': 0,
                'exhale': 0,
                'pause': 0,
                'description': 'Meditación de atención plena enfocada en respiración natural.',
                'benefits': ['Mejora atención', 'Reduce pensamientos dispersos', 'Aumenta awareness'],
                'instructions': [
                    'Siéntate con la espalda recta pero relajada',
                    'Cierra los ojos suavemente',
                    'Enfócate en tu respiración natural',
                    'Cuando la mente divague, regresa gentilmente',
                    'No juzgues tus pensamientos, solo observa',
                    'Mantén una actitud de curiosidad amable'
                ]
            },
            'mindfulness_10': {
                'name': 'Atención Plena 10 minutos',
                'duration': 10,
                'cycles': 1,
                'inhale': 0,
                'hold': 0,
                'exhale': 0,
                'pause': 0,
                'description': 'Meditación extendida para preparación mental profunda.',
                'benefits': ['Concentración profunda', 'Calma mental duradera', 'Mayor autoconciencia'],
                'instructions': [
                    'Encuentra un lugar silencioso',
                    'Adopta una postura estable y cómoda',
                    'Comienza notando tu cuerpo y respiración',
                    'Expande la conciencia a sonidos ambientales',
                    'Regresa siempre a la respiración como ancla',
                    'Cultiva una actitud de aceptación'
                ]
            },
            'body_scan': {
                'name': 'Escaneo Corporal',
                'duration': 7,
                'cycles': 1,
                'inhale': 0,
                'hold': 0,
                'exhale': 0,
                'pause': 0,
                'description': 'Relajación progresiva recorriendo todo el cuerpo.',
                'benefits': ['Libera tensión física', 'Mejora conexión mente-cuerpo', 'Profunda relajación'],
                'instructions': [
                    'Acuéstate o siéntate cómodamente',
                    'Comienza por los dedos de los pies',
                    'Nota sensaciones sin cambiar nada',
                    'Muévete lentamente hacia arriba',
                    'Dedica 30-60 segundos a cada parte',
                    'Termina sintiendo todo el cuerpo completo'
                ]
            },
            'loving_kindness': {
                'name': 'Bondad Amorosa (Metta)',
                'duration': 6,
                'cycles': 1,
                'inhale': 0,
                'hold': 0,
                'exhale': 0,
                'pause': 0,
                'description': 'Cultiva sentimientos positivos hacia ti y otros.',
                'benefits': ['Mejora autoestima', 'Reduce autocrítica', 'Aumenta compasión'],
                'instructions': [
                    'Comienza enviándote buenos deseos a ti mismo',
                    'Usa frases como "Que sea feliz, que esté en paz"',
                    'Extiende estos deseos a personas queridas',
                    'Incluye gradualmente a personas neutras',
                    'Finalmente incluye a personas difíciles',
                    'Termina enviando bondad a todos los seres'
                ]
            }
        }
        
        # Estado actual
        self.current_technique = None
        self.remaining_time = 0
        self.is_active = False
        self.start_time = None
        self.current_cycle = 0
        self.breathing_phase = 'inhale'  # 'inhale', 'hold', 'exhale', 'pause'
        self.breathing_count = 0
        self.session_history = []
    
    def get_available_techniques(self) -> Dict[str, Any]:
        """Retorna las técnicas disponibles"""
        return self.techniques
    
    def start_technique(self, technique_key: str) -> Dict[str, Any]:
        """Inicia una técnica específica"""
        if technique_key not in self.techniques:
            raise ValueError(f"Técnica '{technique_key}' no encontrada")
        
        self.current_technique = self.techniques[technique_key]
        self.remaining_time = self.current_technique['duration'] * 60
        self.is_active = True
        self.start_time = datetime.now()
        self.current_cycle = 0
        self.breathing_phase = 'inhale'
        self.breathing_count = 0
        
        print(f"🧘 Iniciando: {self.current_technique['name']}")
        print(f"📝 {self.current_technique['description']}")
        self._show_instructions()
        
        return {
            'name': self.current_technique['name'],
            'duration': self.current_technique['duration'],
            'cycles': self.current_technique['cycles']
        }
    
    def _show_instructions(self):
        """Muestra las instrucciones de la técnica"""
        print("\n📋 INSTRUCCIONES:")
        for i, instruction in enumerate(self.current_technique['instructions'], 1):
            print(f"  {i}. {instruction}")
        print()
    
    def tick(self):
        """Reduce el tiempo en 1 segundo y maneja las fases de respiración"""
        if not self.is_active or self.remaining_time <= 0:
            return
        
        self.remaining_time -= 1
        
        # Manejar técnicas de respiración estructurada
        if self.current_technique['inhale'] > 0:
            self._handle_breathing_cycle()
    
    def _handle_breathing_cycle(self):
        """Maneja los ciclos de respiración estructurada"""
        technique = self.current_technique
        
        # Duración de cada fase
        phases = {
            'inhale': technique['inhale'],
            'hold': technique['hold'],
            'exhale': technique['exhale'],
            'pause': technique['pause']
        }
        
        current_phase_duration = phases[self.breathing_phase]
        
        if current_phase_duration > 0:
            self.breathing_count += 1
            
            # Cambiar de fase cuando se complete el tiempo
            if self.breathing_count >= current_phase_duration:
                self._next_breathing_phase()
    
    def _next_breathing_phase(self):
        """Cambia a la siguiente fase de respiración"""
        self.breathing_count = 0
        
        phase_order = ['inhale', 'hold', 'exhale', 'pause']
        current_index = phase_order.index(self.breathing_phase)
        
        # Si hay pausa y es > 0, incluirla
        if self.breathing_phase == 'exhale' and self.current_technique['pause'] > 0:
            self.breathing_phase = 'pause'
        elif self.breathing_phase == 'pause' or (self.breathing_phase == 'exhale' and self.current_technique['pause'] == 0):
            self.breathing_phase = 'inhale'
            self.current_cycle += 1
        else:
            next_index = (current_index + 1) % len(phase_order)
            self.breathing_phase = phase_order[next_index]
            
            # Saltar fases con duración 0
            while self.current_technique[self.breathing_phase] == 0 and self.breathing_phase != 'inhale':
                next_index = (phase_order.index(self.breathing_phase) + 1) % len(phase_order)
                self.breathing_phase = phase_order[next_index]
    
    def get_breathing_instruction(self) -> Optional[str]:
        """Retorna la instrucción de respiración actual"""
        if not self.is_active or not self.current_technique:
            return None
        
        # Para técnicas sin respiración estructurada
        if self.current_technique['inhale'] == 0:
            return "Respira naturalmente y mantén la atención en el presente"
        
        phase_instructions = {
            'inhale': f"Inhala suavemente... ({self.breathing_count + 1}/{self.current_technique['inhale']})",
            'hold': f"Mantén el aire... ({self.breathing_count + 1}/{self.current_technique['hold']})",
            'exhale': f"Exhala lentamente... ({self.breathing_count + 1}/{self.current_technique['exhale']})",
            'pause': f"Pausa vacío... ({self.breathing_count + 1}/{self.current_technique['pause']})"
        }
        
        base_instruction = phase_instructions.get(self.breathing_phase, "")
        cycle_info = f" | Ciclo: {self.current_cycle + 1}/{self.current_technique['cycles']}"
        
        return base_instruction + cycle_info
    
    def get_remaining_time(self) -> int:
        """Retorna el tiempo restante en segundos"""
        return max(0, self.remaining_time)
    
    def pause(self):
        """Pausa la meditación"""
        self.is_active = False
        print("⏸️ Meditación pausada - Respira naturalmente")
    
    def resume(self):
        """Reanuda la meditación"""
        self.is_active = True
        print("▶️ Meditación reanudada")
    
    def reset(self):
        """Reinicia la meditación"""
        if self.current_technique:
            self.remaining_time = self.current_technique['duration'] * 60
            self.current_cycle = 0
            self.breathing_phase = 'inhale'
            self.breathing_count = 0
            self.is_active = True
            print("🔄 Meditación reiniciada")
    
    def stop(self):
        """Detiene la meditación"""
        self.is_active = False
        if self.current_technique and self.start_time:
            self.save_session_to_history()
        self.current_technique = None
        print("⏹️ Meditación completada")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de la sesión actual"""
        if not self.start_time:
            return {}
        
        elapsed = datetime.now() - self.start_time
        return {
            'technique': self.current_technique['name'] if self.current_technique else None,
            'elapsed_minutes': int(elapsed.total_seconds() / 60),
            'cycles_completed': self.current_cycle,
            'remaining_seconds': self.remaining_time,
            'breathing_phase': self.breathing_phase
        }
    
    def save_session_to_history(self):
        """Guarda la sesión al historial"""
        if self.start_time and self.current_technique:
            duration = (datetime.now() - self.start_time).total_seconds() / 60
            session_data = {
                'date': datetime.now().isoformat(),
                'technique': self.current_technique['name'],
                'planned_duration': self.current_technique['duration'],
                'actual_duration': duration,
                'cycles_completed': self.current_cycle,
                'completion_rate': min(100, (duration / self.current_technique['duration']) * 100)
            }
            self.session_history.append(session_data)
            print(f"💾 Sesión de meditación guardada")
    
    def get_meditation_benefits(self, technique_key: str) -> List[str]:
        """Retorna los beneficios de una técnica específica"""
        if technique_key in self.techniques:
            return self.techniques[technique_key].get('benefits', [])
        return []
    
    def get_pre_study_recommendation(self) -> str:
        """Recomienda una técnica basada en el momento del día y objetivos"""
        now = datetime.now()
        hour = now.hour
        
        if 6 <= hour < 12:  # Mañana
            return 'box_breathing'  # Para energizar y enfocar
        elif 12 <= hour < 18:  # Tarde
            return 'breathing_4_7_8'  # Para calmar y refocus
        else:  # Noche
            return 'mindfulness_5'  # Para relajar sin sobreestimular
    
    def get_daily_streak(self) -> int:
        """Calcula la racha diaria de meditación"""
        if not self.session_history:
            return 0
        
        # Ordenar sesiones por fecha
        sorted_sessions = sorted(
            self.session_history,
            key=lambda x: datetime.fromisoformat(x['date']),
            reverse=True
        )
        
        streak = 0
        current_date = datetime.now().date()
        
        for session in sorted_sessions:
            session_date = datetime.fromisoformat(session['date']).date()
            
            if session_date == current_date:
                if streak == 0:  # Primera sesión del día actual
                    streak = 1
                current_date -= timedelta(days=1)
            elif session_date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def get_mindfulness_quote(self) -> str:
        """Retorna una cita inspiracional sobre mindfulness"""
        quotes = [
            "La mente que no juzga es la mente más sabia. - Jon Kabat-Zinn",
            "El momento presente es el único momento disponible para nosotros. - Thich Nhat Hanh",
            "Donde quiera que vayas, ahí estás. - Jon Kabat-Zinn",
            "La meditación no se trata de sentirse de cierta manera. Se trata de sentir como te sientes. - Dan Harris",
            "La respiración es el puente que conecta la vida con la conciencia. - Thich Nhat Hanh",
            "No puedes detener las olas, pero puedes aprender a surfear. - Jon Kabat-Zinn",
            "La paz viene del interior. No la busques afuera. - Buddha",
            "El arte de vivir radica en un delicado equilibrio entre soltar y aguantar. - Rumi"
        ]
        
        import random
        return random.choice(quotes)
    
    def suggest_post_meditation_activity(self) -> str:
        """Sugiere una actividad después de la meditación"""
        activities = [
            "📝 Escribe 3 cosas por las que te sientes agradecido",
            "🎯 Define tu intención principal para la sesión de estudio",
            "💧 Bebe un vaso de agua mindfully",
            "📚 Organiza tu espacio de estudio con atención plena",
            "🎵 Selecciona música apropiada para concentrarte",
            "📱 Apaga notificaciones por el tiempo de estudio",
            "🕯️ Enciende una vela o incienso para el ambiente",
            "📖 Lee un párrafo inspiracional sobre tu tema de estudio"
        ]
        
        import random
        return random.choice(activities)