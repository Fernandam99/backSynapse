#!/usr/bin/env python3
"""
Sistema de Temporizadores para Técnicas de Concentración y Meditación
Archivo Base - Inicialización y Control Principal
"""

import time
import sys
from datetime import datetime, timedelta
from study_techniques import StudyTimer
from meditation_techniques import MeditationTimer

class TimerManager:
    """Gestor principal del sistema de temporizadores"""
    
    def __init__(self):
        self.study_timer = StudyTimer()
        self.meditation_timer = MeditationTimer()
        self.current_session = None
        self.is_paused = False
        self.session_stats = {
            'sessions_today': 0,
            'total_minutes': 0,
            'streak_days': 0,
            'best_streak': 0
        }
    
    def show_menu(self):
        """Muestra el menú principal"""
        print("\n" + "="*60)
        print("🧠 SISTEMA DE CONCENTRACIÓN Y MEDITACIÓN 🧠")
        print("="*60)
        print("1. Técnicas de Estudio")
        print("2. Técnicas de Meditación")
        print("3. Ver Estadísticas")
        print("4. Configurar Pausa Personalizada")
        print("5. Salir")
        print("-"*60)
    
    def show_study_techniques(self):
        """Muestra las técnicas de estudio disponibles"""
        print("\n📚 TÉCNICAS DE ESTUDIO:")
        techniques = self.study_timer.get_available_techniques()
        for i, (key, info) in enumerate(techniques.items(), 1):
            print(f"{i}. {info['name']}")
            print(f"   ⏰ {info['work']}min trabajo / {info['break']}min descanso")
        print("0. Volver al menú principal")
    
    def show_meditation_techniques(self):
        """Muestra las técnicas de meditación disponibles"""
        print("\n🧘 TÉCNICAS DE MEDITACIÓN:")
        techniques = self.meditation_timer.get_available_techniques()
        for i, (key, info) in enumerate(techniques.items(), 1):
            print(f"{i}. {info['name']}")
            print(f"   ⏰ {info['duration']}min - {info['description']}")
        print("0. Volver al menú principal")
    
    def start_study_session(self, technique_key):
        """Inicia una sesión de estudio"""
        try:
            self.current_session = self.study_timer.start_technique(technique_key)
            self.run_timer_session('study')
        except Exception as e:
            print(f"❌ Error al iniciar sesión: {e}")
    
    def start_meditation_session(self, technique_key):
        """Inicia una sesión de meditación"""
        try:
            self.current_session = self.meditation_timer.start_technique(technique_key)
            self.run_timer_session('meditation')
        except Exception as e:
            print(f"❌ Error al iniciar sesión: {e}")
    
    def run_timer_session(self, session_type):
        """Ejecuta una sesión de temporizador"""
        if not self.current_session:
            return
        
        print(f"\n🚀 Iniciando: {self.current_session['name']}")
        print("Controles: [ESPACIO] Pausar/Reanudar | [Q] Salir | [R] Reiniciar")
        
        phase = 'work' if session_type == 'study' else 'session'
        
        while True:
            if session_type == 'study':
                remaining = self.study_timer.get_remaining_time()
                current_phase = self.study_timer.get_current_phase()
            else:
                remaining = self.meditation_timer.get_remaining_time()
                current_phase = phase
            
            if remaining <= 0:
                if session_type == 'study' and self.study_timer.has_next_phase():
                    print(f"\n✅ Fase completada! Cambiando a {self.study_timer.get_next_phase()}")
                    self.study_timer.next_phase()
                    continue
                else:
                    self.complete_session()
                    break
            
            self.display_timer(remaining, current_phase, session_type)
            
            # Simular entrada de teclado (en implementación real usarías threading)
            time.sleep(1)
            
            if not self.is_paused:
                if session_type == 'study':
                    self.study_timer.tick()
                else:
                    self.meditation_timer.tick()
    
    def display_timer(self, remaining, phase, session_type):
        """Muestra el temporizador en pantalla"""
        minutes = remaining // 60
        seconds = remaining % 60
        
        phase_emoji = "🔥" if phase == 'work' else "☕" if phase == 'break' else "🧘"
        phase_name = phase.title() if session_type == 'study' else 'Meditación'
        
        # Clear screen (simplificado)
        print("\033[2J\033[H", end="")
        print(f"\n{phase_emoji} {phase_name}")
        print(f"⏰ {minutes:02d}:{seconds:02d}")
        print(f"📊 Sesión: {self.current_session['name']}")
        
        if session_type == 'meditation' and hasattr(self.meditation_timer, 'get_breathing_instruction'):
            instruction = self.meditation_timer.get_breathing_instruction()
            if instruction:
                print(f"🫁 {instruction}")
    
    def complete_session(self):
        """Completa la sesión actual"""
        print("\n🎉 ¡Sesión completada!")
        self.session_stats['sessions_today'] += 1
        
        if self.current_session:
            duration = self.current_session.get('work', self.current_session.get('duration', 0))
            self.session_stats['total_minutes'] += duration
        
        print(f"✅ Sesiones hoy: {self.session_stats['sessions_today']}")
        print(f"⏱️  Total minutos: {self.session_stats['total_minutes']}")
        
        self.current_session = None
    
    def show_stats(self):
        """Muestra las estadísticas del usuario"""
        print("\n📈 ESTADÍSTICAS")
        print("-"*30)
        print(f"🔥 Racha actual: {self.session_stats['streak_days']} días")
        print(f"⭐ Mejor racha: {self.session_stats['best_streak']} días")
        print(f"✅ Sesiones hoy: {self.session_stats['sessions_today']}")
        print(f"⏱️  Minutos totales: {self.session_stats['total_minutes']}")
        print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    
    def configure_custom_pause(self):
        """Configura pausas personalizadas"""
        print("\n⚙️ CONFIGURACIÓN DE PAUSAS")
        try:
            work_time = int(input("Tiempo de trabajo (minutos): "))
            break_time = int(input("Tiempo de descanso (minutos): "))
            
            if work_time > 0 and break_time > 0:
                self.study_timer.add_custom_technique(work_time, break_time)
                print(f"✅ Técnica personalizada creada: {work_time}min/{break_time}min")
            else:
                print("❌ Los tiempos deben ser mayores a 0")
        except ValueError:
            print("❌ Por favor ingresa números válidos")
    
    def run(self):
        """Ejecuta el programa principal"""
        print("🚀 Iniciando Sistema de Concentración y Meditación...")
        
        while True:
            self.show_menu()
            try:
                choice = input("Selecciona una opción: ").strip()
                
                if choice == '1':
                    self.handle_study_menu()
                elif choice == '2':
                    self.handle_meditation_menu()
                elif choice == '3':
                    self.show_stats()
                elif choice == '4':
                    self.configure_custom_pause()
                elif choice == '5':
                    print("👋 ¡Hasta luego! Mantén tu concentración.")
                    break
                else:
                    print("❌ Opción no válida")
                    
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego! Mantén tu concentración.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def handle_study_menu(self):
        """Maneja el menú de técnicas de estudio"""
        while True:
            self.show_study_techniques()
            choice = input("Selecciona una técnica: ").strip()
            
            if choice == '0':
                break
            
            try:
                technique_index = int(choice) - 1
                techniques = list(self.study_timer.get_available_techniques().keys())
                
                if 0 <= technique_index < len(techniques):
                    technique_key = techniques[technique_index]
                    self.start_study_session(technique_key)
                    break
                else:
                    print("❌ Opción no válida")
            except ValueError:
                print("❌ Por favor ingresa un número válido")
    
    def handle_meditation_menu(self):
        """Maneja el menú de técnicas de meditación"""
        while True:
            self.show_meditation_techniques()
            choice = input("Selecciona una técnica: ").strip()
            
            if choice == '0':
                break
            
            try:
                technique_index = int(choice) - 1
                techniques = list(self.meditation_timer.get_available_techniques().keys())
                
                if 0 <= technique_index < len(techniques):
                    technique_key = techniques[technique_index]
                    self.start_meditation_session(technique_key)
                    break
                else:
                    print("❌ Opción no válida")
            except ValueError:
                print("❌ Por favor ingresa un número válido")

def main():
    """Función principal"""
    timer_manager = TimerManager()
    timer_manager.run()

if __name__ == "__main__":
    main()