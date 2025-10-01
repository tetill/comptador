#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicatiu LA RENAIXENÇA - Optimized Version
Timer application for radio show production with audio player and presidents game.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import time
from datetime import datetime
import sys
import webbrowser
import urllib.parse
import threading
import os
from functools import lru_cache
from typing import Optional, List, Dict, Any

# Imports per al reproductor d'àudio
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False
    print("tkinterdnd2 no disponible. Drag and drop no funcionarà.")

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Pygame no disponible. El reproductor d'àudio no funcionarà.")

try:
    import vlc
    # Test if VLC can actually be initialized with quiet options
    test_instance = vlc.Instance('--intf', 'dummy', '--no-video', '--quiet', '--no-osd')
    if test_instance:
        VLC_AVAILABLE = True
        print("VLC disponible i funcional")
    else:
        VLC_AVAILABLE = False
        print("VLC importat però no funcional")
except Exception as e:
    VLC_AVAILABLE = False
    print(f"VLC no disponible: {e}")


class PrecisionTimer:
    """Timer de precisió per cronometrar seccions."""
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.accumulated_time: float = 0.0
        self.is_running: bool = False
        self.sections: List[Dict[str, Any]] = []
        self.total_time: int = 0
        self.target_time: int = 46 * 60
        self.program_number: str = ""
        
    def start(self) -> bool:
        """Inicia el timer."""
        if not self.is_running:
            self.start_time = time.perf_counter()
            self.is_running = True
            return True
        return False
    
    def stop(self) -> bool:
        """Para el timer."""
        if self.is_running:
            now = time.perf_counter()
            elapsed = now - self.start_time
            self.accumulated_time += elapsed
            self.is_running = False
            self.start_time = None
            return True
        return False
    
    def reset(self) -> None:
        """Reinicia el timer."""
        self.is_running = False
        self.start_time = None
        self.accumulated_time = 0.0
    
    def get_current_time(self) -> int:
        """Obté el temps actual en segons."""
        if self.is_running and self.start_time:
            now = time.perf_counter()
            elapsed = now - self.start_time
            return int(self.accumulated_time + elapsed)
        return int(self.accumulated_time)
    
    def add_section(self, name: str, duration: int) -> int:
        """Afegeix una nova secció."""
        section = {
            'name': name, 
            'duration': duration, 
            'timestamp': datetime.now().isoformat()
        }
        self.sections.append(section)
        self.total_time += duration
        return len(self.sections)
    
    def remove_section(self, index: int) -> bool:
        """Elimina una secció per índex."""
        if 0 <= index < len(self.sections):
            removed = self.sections.pop(index)
            self.total_time -= removed['duration']
            return True
        return False
    
    @lru_cache(maxsize=1)
    def get_catalan_date(self) -> str:
        """Obté la data en català (cached)."""
        now = datetime.now()
        dies_setmana = ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte", "Diumenge"]
        mesos = ["", "gener", "febrer", "març", "abril", "maig", "juny", "juliol", "agost", "setembre", "octubre", "novembre", "desembre"]
        return f"{dies_setmana[now.weekday()]}, {now.day} de {mesos[now.month]} de {now.year}"
    
    def export_sections(self) -> str:
        """Exporta les seccions a text."""
        if not self.sections:
            return ""
        
        now = datetime.now()
        lines = [
            f"REGISTRE LA RENAIXENÇA PGM {self.program_number}",
            "=" * 50,
            f"Data: {self.get_catalan_date()}",
            f"Hora: {now.strftime('%H:%M:%S')}",
            "",
            "Nº  | Secció                           | Durada",
            "-" * 50
        ]
        
        for i, section in enumerate(self.sections):
            num = str(i + 1).rjust(2)
            name = section['name'][:35].ljust(35)
            duration = self.format_time(section['duration'])
            lines.append(f"{num}  | {name} | {duration}")
        
        lines.extend([
            "-" * 50,
            f"TOTAL: {len(self.sections)} seccions - {self.format_time(self.total_time)}"
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_time(seconds: int) -> str:
        """Formata segons a MM:SS."""
        return f"{int(seconds) // 60:02d}:{int(seconds) % 60:02d}"


class PresidentsGame:
    """Joc dels presidents de la Generalitat."""
    
    def __init__(self):
        self.presidents = [
            "133. Salvador Illa Roca (2024-)",
            "132. Pere Aragonès Garcia (2021-2024)",
            "131. Joaquim Torra Pla (2018-2020)",
            "130. Carles Puigdemont Casamajó (2016-2017)",
            "129. Artur Mas Gavarró (2010-2016)",
            "128. José Montilla Aguilera (2006-2010)",
            "127. Pasqual Maragall Mira (2003-2006)",
            "126. Jordi Pujol Soley (1980-2003)",
            "125. Josep Tarradellas Joan (1954-1980)",
            "124. Josep Irla Bosch (1940-1954)",
            "123. Lluís Companys Jover (1933-1940)",
            "122. Francesc Macià Llussà (1932-1933)",
            "121. Josep de Vilamala (1713-1714)",
            "120. Francesc Antoni de Solanell (1710-1713)",
            "119. Manuel de Copons D'Esquerrer (1707-1710)",
            "118. Josep Grau (1706-1707)",
            "117. Francesc de Valls Freixa (1704-1705)",
            "116. Antoni de Planella (1701-1704)",
            "116. Josep Antoni Valls Pandutxo (1701)",
            "115. Climent de Solanell de Foix (1698-1701)",
            "114. Rafael de Pinyana Galvany (1695-1698)",
            "113. Antoni de Planella de Cruïlles (1692-1695)",
            "112. Benet Ignasi de Salazar (1689-1692)",
            "111. Antoni de Saiol de Quarteroni (1686-1689)",
            "110. Baltasar de Muntaner de Sacosta (1683-1686)",
            "109. Josep Sastre Prats (1680-1683)",
            "108. Alfonso de Sotomayor (1677-1680)",
            "107. Esteve Mercadal Dou (1674-1677)",
            "106. Josep de Camporrells de Sabater (1671-1674)",
            "105. Joan Pagès Vallgornera (1668-1671)",
            "104. Josep de Magarola de Grau (1665-1668)",
            "103. Jaume de Copons de Tamarit (1662-1665)",
            "102. Pau d'Àger d'Orcau (1659-1662)",
            "101. Joan Jeroni Besora (1656-1659)",
            "100. Francesc Pijoan (1654-1656)",
            "99. Pau del Rosso (1650-1654)",
            "98. Andreu Pont (1647-1650)",
            "97. Gispert d'Amat i Desbosc de Sant Vicenç (1644-1647)",
            "96. Bernat de Cardona i de Raset (1641-1644)",
            "95. Josep Soler (1641)",
            "94. Pau Claris Casademunt (1638-1641)",
            "93. Miquel d'Alentorn i Salbà (1635-1638)",
            "92. Garcia Gil de Manrique y Maldonado (1632-1635)",
            "91. Esteve Salacruz (1632)",
            "90. Pere Antoni Serra (1629-1632)",
            "89. Francesc Morillo (1626-1629)",
            "88. Pere de Magarola i Fontanet (1623-1626)",
            "87. Benet Fontanella (1620-1623)",
            "86. Lluís de Tena Gomez (1617-1620)",
            "85. Miquel d'Aimeric i de Codina (1616-1617)",
            "84. Ramon d'Olmera i d'Alemany (1614-1616)",
            "83. Francesc de Sentjust i de Castre (1611-1614)",
            "82. Onofre d'Alentorn i de Botella (1608-1611)",
            "81. Pere Pau Caçador i d'Aguilar-Dusai (1605-1608)",
            "80. Bernat de Cardona i de Queralt (1602-1605)",
            "79. Jaume Cordelles i Oms (1599-1602)",
            "78. Francesc Oliveres (1598-1599)",
            "Francesc Oliver de Boteller (1596-1598)",
            "77. Miquel d'Agullana (1593-1596)",
            "76. Jaume Caçador Claret (1590-1593)",
            "75. Francesc Oliver de Boteller (1587-1588)",
            "74. Martí Joan de Calders (1587)",
            "Pere Oliver Boteller de Riquer (1584-1587)",
            "73. Jaume Beuló (1584)",
            "72. Rafael d'Oms (1581-1584)",
            "Benet de Tocco (1578-1581)",
            "71. Pere Oliver Boteller de Riquer (1575-1578)",
            "70. Jaume Cerveró (1572-1575)",
            "69. Benet de Tocco (1569-1572)",
            "68. Francesc Giginta (1566-1569)",
            "67. Onofre Gomis (1563-1566)",
            "Miquel d'Oms de Sentmenat (1560-1563)",
            "66. Ferran de Loaces Peres (1559-1560)",
            "65. Pere Àngel Ferrer Despuig (1557-1559)",
            "64. Francesc Jeroni Benet Franc (1554-1557)",
            "63. Miquel de Tormo (1553-1554)",
            "62. Joan de Tormo (1552-1553)",
            "61. Miquel de Ferrer de Marimon (1552)",
            "60. Onofre de Copons de Vilafranca (1551-1552)",
            "59. Miquel d'Oms de Sentmenat (1548-1551)",
            "58. Jaume Caçador (1545-1548)",
            "57. Miquel Puig (1542-1545)",
            "56. Jeroni de Requesens Roís de Liori (1539-1542)",
            "55. Joan Pasqual (1536-1539)",
            "54. Dionís de Carcassona (1533-1536)",
            "53. Francesc Oliver de Boteller (1530-1533)",
            "52. Francesc de Solsona (1527-1530)",
            "51. Lluís de Cardona Enríquez (1524-1527)",
            "50. Joan Margarit de Requesens (1521-1524)",
            "49. Bernat de Corbera (1518-1521)",
            "48. Esteve de Garret (1515-1518)",
            "47. Jaume Fiella (1514-1515)",
            "46. Joan d'Aragó (1512-1514)",
            "45. Jordi Sanç (1509-1512)",
            "44. Lluís Desplà i d'Oms (1506-1509)",
            "43. Gonzalo Fernández de Heredia (1504-1506)",
            "42. Ferrer Nicolau de Gualbes i Desvalls (1503-1504)",
            "41. Alfons d'Aragó (1500-1503)",
            "40. Pedro de Mendoza (1497-1500)",
            "39. Francí Vicenç (1494-1497)",
            "38. Joan de Peralta (1491-1494)",
            "37. Juan Payo Coello (1488-1491)",
            "Ponç Andreu de Vilar (1485-1488)",
            "36. Pere de Cardona (1482-1485)",
            "35. Berenguer de Sos (1479-1482)",
            "34. Pere Joan Llobera (1478-1479)",
            "33. Miquel Delgado (1476-1478)",
            "32. Joan Maurici de Ribes (1473-1476)",
            "31. Miquel Samsó (1470-1473)",
            "30. Ponç Andreu de Vilar (1467-1470)",
            "29. Francesc Colom (1464-1467)",
            "Bernat Saportella (1463-1472)",
            "28. Manuel de Montsuar i Mateu (1461-1464)",
            "27. Antoni Pere Ferrer (1458-1461)",
            "26. Nicolau Pujades (1455-1458)",
            "25. Bernat Guillem Samasó (1452-1455)",
            "24. Bertran Samasó (1449-1452)",
            "23. Pero Ximénez de Urrea i de Bardaixí (1446-1449)",
            "22. Jaume de Cardona i de Gandía (1443-1446)",
            "21. Antoni d'Avinyó i de Moles (1440-1443)",
            "20. Pere de Darnius (1437-1440)",
            "19. Pere de Palou (1434-1437)",
            "Marc de Vilalba (1431-1434)",
            "18. Domènec Ram i Lanaja (1428-1431)",
            "17. Felip de Malla (1425-1428)",
            "16. Dalmau de Cartellà i Despou (1422-1425)",
            "15. Joan Desgarrigues (1419-1422)",
            "14. Andreu Bertran (1416-1419)",
            "13. Marc de Vilalba (1414-1416)",
            "12. Alfons de Tous (1396-1413)",
            "11. Miquel de Santjoan (1389-1396)",
            "10. Arnau Descolomer (1384-1389)",
            "9. Pere de Santamans (1381-1383)",
            "8. Felip d'Anglesola (1380)",
            "Ramon Gener (1379-1380)",
            "7. Galceran de Besora i de Cartellà (1377-1378)",
            "6. Guillem de Guimerà i d'Abella (1376-1377)",
            "5. Joan I d'Empúries (1376)",
            "Romeu Sescomes (1375-1376)",
            "4. Bernat Vallès (1365-1367)",
            "3. Ramon Gener (1364-1365)",
            "2. Ramon Sescomes (1363-1364)",
            "1. Berenguer de Cruïlles (1359-1362)"
        ]
        self.current_index: int = 0
        self.completed: List[str] = []

    def get_current_president(self) -> str:
        """Obté el president actual."""
        if self.current_index < len(self.presidents):
            return self.presidents[self.current_index]
        return "COMPLETAT!"

    def mark_correct(self) -> bool:
        """Marca el president actual com a correcte."""
        if self.current_index < len(self.presidents):
            self.completed.append(self.presidents[self.current_index])
            self.current_index += 1
            return True
        return False

    def reset_game(self) -> None:
        """Reinicia el joc."""
        self.current_index = 0
        self.completed = []
    
    def get_progress(self) -> str:
        """Obté el progrés actual."""
        return f"{len(self.completed)}/{len(self.presidents)}"
    
    def is_completed(self) -> bool:
        """Comprova si el joc està completat."""
        return self.current_index >= len(self.presidents)


class AudioPlayer:
    """Reproductor d'àudio amb suport per VLC i Pygame."""
    
    def __init__(self):
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.current_file: Optional[str] = None
        self.current_position: int = 0
        self.duration: int = 0
        self.files: List[str] = []
        self.volume: float = 0.7
        self.start_time: Optional[float] = None
        self.pause_time: float = 0
        self.vlc_instance = None
        self.vlc_player = None
        self.use_vlc: bool = VLC_AVAILABLE
        
        self._initialize_audio_backend()
    
    def _initialize_audio_backend(self) -> None:
        """Inicialitza el backend d'àudio amb fallback robust."""
        # Primer prova VLC si està disponible
        if self.use_vlc and VLC_AVAILABLE:
            try:
                # Usa les mateixes opcions silencioses que en la detecció inicial
                self.vlc_instance = vlc.Instance('--intf', 'dummy', '--no-video', '--quiet', '--no-osd', '--no-stats')
                self.vlc_player = self.vlc_instance.media_player_new()
                self.vlc_player.audio_set_volume(70)
                print("VLC inicialitzat correctament")
            except Exception as e:
                print(f"Error inicialitzant VLC: {e}")
                self.use_vlc = False
                self.vlc_instance = None
                self.vlc_player = None
        
        # Si VLC falla o no està disponible, usa Pygame
        if not self.use_vlc and PYGAME_AVAILABLE:
            try:
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
                print("Pygame inicialitzat correctament com a fallback")
            except Exception as e:
                print(f"Error inicialitzant pygame: {e}")
        
        # Informa sobre l'estat final
        if not self.use_vlc and not PYGAME_AVAILABLE:
            print("ADVERTÈNCIA: Cap reproductor d'àudio disponible!")
        elif not self.use_vlc:
            print("Usant Pygame per reproducció d'àudio (funcionalitat limitada)")
    
    def load_file(self, file_path: str) -> bool:
        """Carrega un fitxer d'àudio."""
        if not os.path.exists(file_path):
            print(f"Fitxer no trobat: {file_path}")
            return False
        
        self.current_file = file_path
        
        if self.use_vlc:
            return self._load_with_vlc(file_path)
        elif PYGAME_AVAILABLE:
            return self._load_with_pygame(file_path)
        
        return False
    
    def _load_with_vlc(self, file_path: str) -> bool:
        """Carrega fitxer amb VLC."""
        try:
            media = self.vlc_instance.media_new(file_path)
            self.vlc_player.set_media(media)
            media.parse()
            self.duration = media.get_duration() / 1000
            return True
        except Exception as e:
            print(f"Error carregant amb VLC: {e}")
            return False
    
    def _load_with_pygame(self, file_path: str) -> bool:
        """Carrega fitxer amb Pygame."""
        try:
            pygame.mixer.music.load(file_path)
            if file_path not in self.files:
                self.files.append(file_path)
            return True
        except Exception as e:
            print(f"Error carregant amb pygame: {e}")
            return False

    def play(self) -> bool:
        """Reprodueix l'àudio."""
        if not self.current_file:
            return False
        
        if self.use_vlc:
            return self._play_with_vlc()
        elif PYGAME_AVAILABLE:
            return self._play_with_pygame()
        
        return False
    
    def _play_with_vlc(self) -> bool:
        """Reprodueix amb VLC."""
        try:
            if self.is_paused:
                self.vlc_player.pause()
                self.is_paused = False
            else:
                self.vlc_player.play()
            self.is_playing = True
            return True
        except Exception as e:
            print(f"Error reproduint amb VLC: {e}")
            return False
    
    def _play_with_pygame(self) -> bool:
        """Reprodueix amb Pygame."""
        try:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.start_time = time.time() - self.pause_time
            else:
                pygame.mixer.music.play()
                self.start_time = time.time()
                self.pause_time = 0
            self.is_playing = True
            return True
        except Exception as e:
            print(f"Error reproduint: {e}")
            return False
    
    def pause(self) -> bool:
        """Pausa la reproducció."""
        if self.use_vlc and self.vlc_player:
            if self.is_playing and not self.is_paused:
                self.vlc_player.pause()
                self.is_paused = True
                return True
        elif PYGAME_AVAILABLE:
            if self.is_playing and not self.is_paused:
                pygame.mixer.music.pause()
                self.is_paused = True
                if self.start_time:
                    self.pause_time = time.time() - self.start_time
                return True
        return False
    
    def stop(self) -> bool:
        """Para la reproducció."""
        if self.use_vlc and self.vlc_player:
            self.vlc_player.stop()
            self.is_playing = False
            self.is_paused = False
            return True
        elif PYGAME_AVAILABLE:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.current_position = 0
            self.pause_time = 0
            self.start_time = None
            return True
        return False
    
    def get_current_time(self) -> float:
        """Obté el temps actual de reproducció amb precisió de mil·lisegons."""
        if self.use_vlc and self.vlc_player:
            return self.vlc_player.get_time() / 1000.0
        
        if not self.is_playing and not self.is_paused:
            return 0.0
        if self.is_paused:
            return self.pause_time
        elif self.start_time:
            return time.time() - self.start_time
        return 0.0
    
    def set_volume(self, volume: float) -> bool:
        """Estableix el volum."""
        self.volume = max(0.0, min(1.0, volume))
        
        if self.use_vlc and self.vlc_player:
            vlc_volume = int(self.volume * 100)
            self.vlc_player.audio_set_volume(vlc_volume)
            return True
        elif PYGAME_AVAILABLE:
            pygame.mixer.music.set_volume(self.volume)
            return True
        
        return False
    
    def get_status(self) -> str:
        """Obté l'estat actual."""
        if self.use_vlc and self.vlc_player:
            state = self.vlc_player.get_state()
            if state == vlc.State.Playing:
                return "playing"
            elif state == vlc.State.Paused:
                return "paused"
            else:
                return "stopped"
        elif PYGAME_AVAILABLE:
            if pygame.mixer.music.get_busy():
                return "paused" if self.is_paused else "playing"
            elif self.is_paused:
                return "paused"
            else:
                return "stopped"
        return "unavailable"
    
    def add_files(self, file_paths: List[str]) -> List[str]:
        """Afegeix fitxers a la llista."""
        added = []
        for file_path in file_paths:
            if (file_path.lower().endswith(('.mp3', '.wav', '.ogg')) and 
                file_path not in self.files):
                self.files.append(file_path)
                added.append(file_path)
        return added

    def remove_file(self, index: int) -> bool:
        """Elimina un fitxer de la llista per índex."""
        if 0 <= index < len(self.files):
            removed_file = self.files.pop(index)
            # Si el fitxer eliminat és el que s'està reproduint, para la reproducció
            if self.current_file == removed_file:
                self.stop()
                self.current_file = None
            return True
        return False

    def remove_file_by_path(self, file_path: str) -> bool:
        """Elimina un fitxer de la llista per ruta."""
        if file_path in self.files:
            index = self.files.index(file_path)
            return self.remove_file(index)
        return False

    def set_position(self, position_percent: float) -> bool:
        """Estableix la posició de reproducció (només VLC)."""
        if self.use_vlc and self.vlc_player:
            self.vlc_player.set_position(position_percent)
            return True
        return False


class TimerApp:
    """Aplicació principal del timer."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicatiu LA RENAIXENÇA")
        self.root.geometry("1200x900")
        self.root.configure(bg='#fafbfc')
        
        # Variables d'estat
        self.drag_data = {"item": "", "y": 0}
        self.guest_name_var = tk.StringVar()
        self._update_job = None
        self._audio_update_job = None
        
        # Components principals
        self.timer = PrecisionTimer()
        self.presidents_game = PresidentsGame()
        self.audio_player = AudioPlayer()
        
        # Inicialització
        self.ask_program_number()
        self.setup_ui()
        self._start_update_loops()
        self.update_presidents_display()
        self.root.focus_set()
    
    def ask_program_number(self) -> None:
        """Demana el número de programa."""
        while True:
            number = simpledialog.askstring(
                "Número de programa", 
                "Introdueix el número del programa (3 dígits, ex: 157):", 
                parent=self.root
            )
            if number is None:
                if not hasattr(self.timer, 'program_number') or not self.timer.program_number:
                    self.timer.program_number = "000"
                return
                
            number = number.strip()
            if len(number) == 3 and number.isdigit():
                self.timer.program_number = number
                break
            else:
                messagebox.showerror(
                    "Error", 
                    "El número de programa ha de tenir exactament 3 dígits (000-999)", 
                    parent=self.root
                )

    def setup_ui(self) -> None:
        """Configura la interfície d'usuari."""
        style = ttk.Style()
        style.configure("Thick.TLabelframe", borderwidth=2, relief="solid")
        
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # Configurar el root per redimensionament
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self._setup_header(main_frame)
        self._setup_current_section(main_frame)
        self._setup_total_time(main_frame)
        self._setup_bottom_sections(main_frame)
        self._setup_presidents_audio(main_frame)
        
        # Habilita drag and drop
        self._enable_audio_drag_drop()
    
    def _setup_header(self, parent) -> None:
        """Configura la capçalera."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(1, weight=1)

        ttk.Label(header_frame, text="Aplicatiu LA RENAIXENÇA", 
                 font=('Arial', 16, 'bold')).grid(row=0, column=0)
        
        self.program_label = ttk.Label(
            header_frame, 
            text=f"PROGRAMA #{self.timer.program_number}", 
            font=('Arial', 12, 'bold')
        )
        self.program_label.grid(row=0, column=1, padx=(20, 0), sticky=tk.W)
        
        ttk.Button(header_frame, text="Canviar Programa", 
                  command=self.restart_program).grid(row=0, column=2, padx=(20, 0))
    
    def _setup_current_section(self, parent) -> None:
        """Configura la secció actual."""
        current_frame = ttk.LabelFrame(parent, text="SECCIÓ ACTUAL", 
                                     padding="15", style="Thick.TLabelframe")
        current_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        current_frame.columnconfigure(0, weight=1)

        current_container = ttk.Frame(current_frame)
        current_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        current_container.columnconfigure(0, weight=1)
        current_container.columnconfigure(1, weight=1)

        left_frame = ttk.Frame(current_container)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        left_frame.columnconfigure(0, weight=1)

        self.section_name_var = tk.StringVar(value="Secció 1")
        ttk.Label(left_frame, text="Nom de la secció:").grid(row=0, column=0, pady=(0, 5), sticky=tk.W)
        section_entry = ttk.Entry(left_frame, textvariable=self.section_name_var)
        section_entry.grid(row=1, column=0, pady=(0, 15), sticky=(tk.W, tk.E))

        controls_frame = ttk.Frame(left_frame)
        controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        for i in range(4):
            controls_frame.columnconfigure(i, weight=1)

        self.start_btn = ttk.Button(controls_frame, text="Iniciar", command=self.start_timer)
        self.start_btn.grid(row=0, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))

        self.stop_btn = ttk.Button(controls_frame, text="Parar", command=self.stop_timer)
        self.stop_btn.grid(row=0, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))

        self.split_btn = ttk.Button(controls_frame, text="Parcial", command=self.split_section)
        self.split_btn.grid(row=0, column=2, padx=2, pady=2, sticky=(tk.W, tk.E))

        self.save_btn = ttk.Button(controls_frame, text="Guardar", command=self.save_section)
        self.save_btn.grid(row=0, column=3, padx=2, pady=2, sticky=(tk.W, tk.E))

        # Comptador dret
        self.current_time_var = tk.StringVar(value="00:00")
        self.current_time_label = ttk.Label(
            current_container, textvariable=self.current_time_var,
            font=('Arial', 32, 'bold')
        )
        self.current_time_label.grid(row=0, column=1, sticky="n")
    
    def _setup_total_time(self, parent) -> None:
        """Configura la secció de temps total."""
        total_frame = ttk.LabelFrame(parent, text="TEMPS TOTAL I RESTANT", 
                                   padding="15", style="Thick.TLabelframe")
        total_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        total_frame.columnconfigure(0, weight=1)

        times_container = ttk.Frame(total_frame)
        times_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        times_container.columnconfigure(0, weight=1)
        times_container.columnconfigure(2, weight=1)

        total_left = ttk.Frame(times_container)
        total_left.grid(row=0, column=0, sticky=tk.W)
        ttk.Label(total_left, text="Temps Total:", font=('Arial', 10, 'bold')).grid(row=0, column=0)
        self.total_time_var = tk.StringVar(value="00:00")
        ttk.Label(total_left, textvariable=self.total_time_var, font=('Arial', 24, 'bold')).grid(row=1, column=0)

        ttk.Separator(times_container, orient='vertical').grid(row=0, column=1, sticky='ns', padx=20)

        total_right = ttk.Frame(times_container)
        total_right.grid(row=0, column=2, sticky=tk.W)
        ttk.Label(total_right, text="Temps Restant:", font=('Arial', 10, 'bold')).grid(row=0, column=0)
        self.remaining_time_var = tk.StringVar(value="46:00")
        self.remaining_label = ttk.Label(total_right, textvariable=self.remaining_time_var, font=('Arial', 24, 'bold'))
        self.remaining_label.grid(row=1, column=0)

        target_frame = ttk.Frame(total_frame)
        target_frame.grid(row=1, column=0, sticky=tk.W, pady=(15, 0))
        self.target_var = tk.StringVar(value="46")

        ttk.Label(target_frame, text="Objectiu:").grid(row=0, column=0)
        ttk.Entry(target_frame, textvariable=self.target_var, width=6).grid(row=0, column=1, padx=(5, 2))
        ttk.Label(target_frame, text="min").grid(row=0, column=2, padx=(0, 5))
        ttk.Button(target_frame, text="Aplicar", command=self.update_target).grid(row=0, column=3)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(total_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, pady=(15, 0), sticky=(tk.W, tk.E))

        buttons_frame = ttk.Frame(total_frame)
        buttons_frame.grid(row=3, column=0, pady=(15, 0), sticky=(tk.W, tk.E))
        for i in range(2):
            buttons_frame.columnconfigure(i, weight=1)

        ttk.Button(buttons_frame, text="Reiniciar Tot", command=self.reset_all).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(buttons_frame, text="Comptador Extra", command=self.open_counter_window).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
    
    def _setup_bottom_sections(self, parent) -> None:
        """Configura les seccions inferiors."""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)
        bottom_frame.rowconfigure(0, weight=1)

        # Manual entry (esquerra)
        manual_frame = ttk.LabelFrame(bottom_frame, text="AFEGIR MANUAL", 
                                    padding="15", style="Thick.TLabelframe")
        manual_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        manual_frame.columnconfigure(0, weight=1)

        manual_content = ttk.Frame(manual_frame)
        manual_content.grid(row=0, column=0, sticky=(tk.W, tk.E))
        manual_content.columnconfigure(0, weight=1)

        ttk.Label(manual_content, text="Nom:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.manual_name_var = tk.StringVar()
        ttk.Entry(manual_content, textvariable=self.manual_name_var).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        time_frame = ttk.Frame(manual_content)
        time_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.manual_min_var = tk.StringVar()
        self.manual_sec_var = tk.StringVar()

        min_frame = ttk.Frame(time_frame)
        min_frame.grid(row=0, column=0, sticky="w", padx=(0, 20))
        ttk.Entry(min_frame, textvariable=self.manual_min_var, width=6).grid(row=0, column=0)
        ttk.Label(min_frame, text="min").grid(row=0, column=1, padx=(2, 0))

        sec_frame = ttk.Frame(time_frame)
        sec_frame.grid(row=0, column=1, sticky="w")
        ttk.Entry(sec_frame, textvariable=self.manual_sec_var, width=6).grid(row=0, column=0)
        ttk.Label(sec_frame, text="seg").grid(row=0, column=1, padx=(2, 0))

        ttk.Button(manual_content, text="Afegir", command=self.add_manual_section).grid(row=3, column=0, sticky=tk.W)

        # Seccions gravades (dreta)
        sections_frame = ttk.LabelFrame(bottom_frame, text="SECCIONS GRAVADES", 
                                      padding="15", style="Thick.TLabelframe")
        sections_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        sections_frame.columnconfigure(0, weight=1)
        sections_frame.rowconfigure(1, weight=1)

        ttk.Button(sections_frame, text="Exportar", command=self.export_sections).grid(row=0, column=0, pady=(0, 10), sticky=tk.W)

        tree_frame = ttk.Frame(sections_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=('num', 'name', 'duration', 'actions'), show='headings')
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=v_scrollbar.set)

        self.tree.heading('num', text='Nº')
        self.tree.heading('name', text='Secció')
        self.tree.heading('duration', text='Temps')
        self.tree.heading('actions', text='Del')

        self.tree.column('num', width=40, anchor='center')
        self.tree.column('name', width=200, anchor='w')
        self.tree.column('duration', width=80, anchor='center')
        self.tree.column('actions', width=40, anchor='center')

        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Eliminar", command=self.delete_selected_section)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Editar nom", command=self.edit_section_name)
        self.context_menu.add_command(label="Editar temps", command=self.edit_section_time)

        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<ButtonPress-1>', self.on_tree_select)
        self.tree.bind('<B1-Motion>', self.on_tree_drag)
        self.tree.bind('<ButtonRelease-1>', self.on_tree_drop)
    
    def _setup_presidents_audio(self, parent) -> None:
        """Configura les seccions de presidents i àudio."""
        presidents_audio_frame = ttk.Frame(parent)
        presidents_audio_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 0))
        
        # Configuració inicial
        presidents_audio_frame.columnconfigure(0, weight=1, uniform="group1")
        presidents_audio_frame.columnconfigure(1, weight=1, uniform="group1")
        presidents_audio_frame.rowconfigure(0, weight=1)

        self._setup_presidents_section(presidents_audio_frame)
        self._setup_audio_section(presidents_audio_frame)
        
    
    def _setup_presidents_section(self, parent) -> None:
        """Configura la secció de presidents."""
        presidents_frame = ttk.LabelFrame(parent, text="PRESIDENTS GENERALITAT", 
                                        padding="15", style="Thick.TLabelframe")
        presidents_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 7))
        presidents_frame.columnconfigure(0, weight=1)
        presidents_frame.rowconfigure(3, weight=1)

        info_frame = ttk.Frame(presidents_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=0)

        ttk.Label(info_frame, text="Convidat:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        guest_entry = ttk.Entry(info_frame, textvariable=self.guest_name_var, width=15)
        guest_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 5))

        ttk.Label(info_frame, text="Ha de dir:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W)
        self.presidents_progress_var = tk.StringVar(value="0/133")
        ttk.Label(info_frame, textvariable=self.presidents_progress_var, 
                 font=('Arial', 10, 'bold'), foreground='blue').grid(row=0, column=3, sticky=tk.E)

        self.current_president_var = tk.StringVar()
        self.current_president_label = ttk.Label(presidents_frame, 
                                               textvariable=self.current_president_var,
                                               font=('Arial', 10, 'normal'),
                                               wraplength=300,
                                               justify='center',
                                               background='#f0f0f0',
                                               relief='sunken',
                                               padding="8")
        self.current_president_label.grid(row=1, column=0, pady=8, sticky=(tk.W, tk.E))

        presidents_buttons_frame = ttk.Frame(presidents_frame)
        presidents_buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 8))
        for i in range(3):
            presidents_buttons_frame.columnconfigure(i, weight=1)

        self.correct_btn = ttk.Button(presidents_buttons_frame, text="Correcte", 
                                     command=self.mark_president_correct)
        self.correct_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 2))

        ttk.Button(presidents_buttons_frame, text="Reiniciar", 
                  command=self.reset_presidents_game).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(2, 2))

        ttk.Button(presidents_buttons_frame, text="Registre", 
                  command=self.export_presidents_record).grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(2, 0))

        completed_frame = ttk.Frame(presidents_frame)
        completed_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        completed_frame.columnconfigure(0, weight=1)
        completed_frame.rowconfigure(0, weight=1)

        self.completed_text = tk.Text(completed_frame, height=10, font=('Arial', 9), 
                                     wrap=tk.WORD, state='disabled', background='#f8f8f8')
        self.completed_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        completed_scroll = ttk.Scrollbar(completed_frame, orient=tk.VERTICAL, 
                                       command=self.completed_text.yview)
        completed_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.completed_text.configure(yscrollcommand=completed_scroll.set)
    
    def _setup_audio_section(self, parent) -> None:
        """Configura la secció d'àudio."""
        audio_frame = ttk.LabelFrame(parent, text="REPRODUCTOR D'ÀUDIO", 
                                   padding="8", style="Thick.TLabelframe")
        audio_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(7, 0))
        audio_frame.columnconfigure(0, weight=1)
        audio_frame.rowconfigure(3, weight=3)

        # Controls audio amb icones
        controls_audio_frame = ttk.Frame(audio_frame)
        controls_audio_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # Botó carregar amb icona
        load_btn = ttk.Button(controls_audio_frame, text="📁", width=3, command=self.load_audio_files)
        load_btn.grid(row=0, column=0, padx=2)

        # Botó play/pause amb icona
        self.play_pause_btn = ttk.Button(controls_audio_frame, text="▶️", width=3, command=self.toggle_play_pause)
        self.play_pause_btn.grid(row=0, column=1, padx=2)

        # Botó stop amb icona
        stop_btn = ttk.Button(controls_audio_frame, text="⏹️", width=3, command=self.stop_audio)
        stop_btn.grid(row=0, column=2, padx=2)

        # Volum simple
        ttk.Label(controls_audio_frame, text="Vol:", font=('Arial', 9)).grid(row=0, column=3, padx=(15, 3))
        self.volume_var = tk.DoubleVar(value=70)
        volume_scale = ttk.Scale(controls_audio_frame, from_=0, to=100, variable=self.volume_var, 
                               orient=tk.HORIZONTAL, length=150, command=self.change_volume)
        volume_scale.grid(row=0, column=4)

        # Temps i barra de progrés (sense línia de fitxer)
        progress_frame = ttk.Frame(audio_frame)
        progress_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        progress_frame.columnconfigure(1, weight=1)

        self.audio_time_var = tk.StringVar(value="00:00 / --:--")
        ttk.Label(progress_frame, textvariable=self.audio_time_var, font=('Courier New', 12, 'bold')).grid(row=0, column=0, sticky=tk.W)

        self.audio_progress_var = tk.DoubleVar()
        self.audio_progress_bar = ttk.Progressbar(progress_frame, variable=self.audio_progress_var, maximum=100)
        self.audio_progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        self.audio_progress_bar.bind("<Button-1>", self.on_progress_click)

        # Separador visual
        ttk.Separator(audio_frame, orient='horizontal').grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 10))

        # Llista fitxers
        files_frame = ttk.Frame(audio_frame)
        files_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(0, weight=1)


        listbox_frame = ttk.Frame(files_frame)
        listbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        self.audio_listbox = tk.Listbox(listbox_frame, font=('Arial', 9))
        self.audio_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        audio_list_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.audio_listbox.yview)
        audio_list_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.audio_listbox.configure(yscrollcommand=audio_list_scrollbar.set)

        self.audio_listbox.bind('<Double-1>', self.on_audio_double_click)
        self.audio_listbox.bind('<Button-3>', self.show_audio_context_menu)
        
        # Context menu per àudio
        self.audio_context_menu = tk.Menu(self.root, tearoff=0)
        self.audio_context_menu.add_command(label="Eliminar", command=self.delete_selected_audio_file)
        self.audio_context_menu.add_separator()
        self.audio_context_menu.add_command(label="Reproduir", command=self.play_selected_audio_file)
        
        # Variable per mantenir el nom del fitxer actual (sense mostrar-lo)
        self.current_audio_var = tk.StringVar(value="Cap fitxer seleccionat")

    
    def _enable_audio_drag_drop(self) -> None:
        """Habilita drag and drop per àudio."""
        if DRAG_DROP_AVAILABLE:
            self.audio_listbox.drop_target_register(DND_FILES)
            self.audio_listbox.dnd_bind('<<Drop>>', self.on_audio_drop)
    
    def _start_update_loops(self) -> None:
        """Inicia els bucles d'actualització."""
        self.update_display()
        self.update_audio_display()
    
    # MÈTODES PRINCIPALS DEL TIMER
    def start_timer(self) -> None:
        """Inicia el timer."""
        self.timer.start()
    
    def stop_timer(self) -> None:
        """Para el timer."""
        self.timer.stop()
    
    def save_section(self) -> None:
        """Guarda la secció actual."""
        current_seconds = self.timer.get_current_time()
        if current_seconds <= 0:
            messagebox.showwarning("Avís", "No hi ha temps!")
            return
        
        section_name = self.section_name_var.get() or f"Secció {len(self.timer.sections) + 1}"
        self.timer.add_section(section_name, current_seconds)
        self.timer.reset()
        self.section_name_var.set(f"Secció {len(self.timer.sections) + 1}")
    
    def split_section(self) -> None:
        """Divideix la secció actual."""
        current_seconds = self.timer.get_current_time()
        if current_seconds <= 0:
            messagebox.showwarning("Avís", "No hi ha temps!")
            return
        
        section_name = self.section_name_var.get() or f"Secció {len(self.timer.sections) + 1}"
        self.timer.add_section(section_name, current_seconds)
        
        if self.timer.is_running:
            self.timer.accumulated_time = 0.0
            self.timer.start_time = time.perf_counter()
        
        self.section_name_var.set(f"Secció {len(self.timer.sections) + 1}")
    
    def add_manual_section(self) -> None:
        """Afegeix una secció manualment."""
        name = self.manual_name_var.get().strip()
        if not name:
            messagebox.showwarning("Avís", "Introdueix nom!")
            return
        
        try:
            minutes = int(self.manual_min_var.get() or "0")
            seconds = int(self.manual_sec_var.get() or "0")
        except ValueError:
            messagebox.showerror("Error", "Valors numèrics!")
            return
        
        if minutes == 0 and seconds == 0:
            messagebox.showwarning("Avís", "Introdueix durada!")
            return
        
        if seconds >= 60:
            messagebox.showerror("Error", "Segons < 60!")
            return
        
        total_duration = minutes * 60 + seconds
        self.timer.add_section(name, total_duration)
        
        # Neteja els camps
        self.manual_name_var.set("")
        self.manual_min_var.set("")
        self.manual_sec_var.set("")
    
    def reset_all(self) -> None:
        """Reinicia tot."""
        if messagebox.askyesno("Reset", "Reiniciar tot?"):
            self.timer.reset()
            self.timer.sections = []
            self.timer.total_time = 0
            self.timer.target_time = 46 * 60
            self.target_var.set("46")
            self.section_name_var.set("Secció 1")
            self.manual_name_var.set("")
            self.manual_min_var.set("")
            self.manual_sec_var.set("")
            self.guest_name_var.set("")
            self.presidents_game.reset_game()
            self.update_presidents_display()
    
    def update_target(self) -> None:
        """Actualitza l'objectiu de temps."""
        try:
            new_target = int(self.target_var.get())
            if new_target < 1 or new_target > 180:
                raise ValueError
            self.timer.target_time = new_target * 60
        except ValueError:
            messagebox.showerror("Error", "1-180 minuts!")
            self.target_var.set(str(self.timer.target_time // 60))
    
    def restart_program(self) -> None:
        """Reinicia el programa."""
        if messagebox.askyesno("Confirmar", "Canviar programa? Es perdran les seccions."):
            self.timer.reset()
            self.timer.sections = []
            self.timer.total_time = 0
            self.timer.target_time = 46 * 60
            self.ask_program_number()
            self.program_label.configure(text=f"PROGRAMA #{self.timer.program_number}")
            self.section_name_var.set("Secció 1")
            self.target_var.set("46")
            self.manual_name_var.set("")
            self.manual_min_var.set("")
            self.manual_sec_var.set("")
            self.guest_name_var.set("")
            self.presidents_game.reset_game()
            self.update_presidents_display()
    
    def open_counter_window(self) -> None:
        """Obre finestra de comptador extra."""
        messagebox.showinfo("Funcionalitat", "Comptador extra no implementat en aquesta versió.")
    
    # MÈTODES D'ACTUALITZACIÓ DE DISPLAY
    def update_display(self) -> None:
        """Actualitza el display principal."""
        current_seconds = self.timer.get_current_time()
        self.current_time_var.set(self.timer.format_time(current_seconds))
        
        total_real_time = self.timer.total_time + current_seconds
        self.total_time_var.set(self.timer.format_time(total_real_time))
        
        progress = min((total_real_time / self.timer.target_time) * 100, 100)
        self.progress_var.set(progress)
        
        remaining = self.timer.target_time - total_real_time
        if remaining > 0:
            self.remaining_time_var.set(self.timer.format_time(remaining))
            self.remaining_label.configure(foreground='blue')
        elif remaining == 0:
            self.remaining_time_var.set("Objectiu!")
            self.remaining_label.configure(foreground='green')
        else:
            self.remaining_time_var.set(f"+{self.timer.format_time(abs(remaining))}")
            self.remaining_label.configure(foreground='red')
        
        self.update_sections_table()
        self.root.after(100, self.update_display)
    
    def update_sections_table(self) -> None:
        """Actualitza la taula de seccions."""
        if self.drag_data.get("item"):
            return
        
        current_selection = self.tree.selection()
        selected_values = None
        if current_selection:
            try:
                selected_values = self.tree.item(current_selection[0], 'values')
            except tk.TclError:
                pass
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, section in enumerate(self.timer.sections):
            item_id = self.tree.insert('', 'end', values=(
                i + 1, 
                section['name'], 
                self.timer.format_time(section['duration']), 
                'X'
            ))
            if (selected_values and len(selected_values) > 1 and 
                selected_values[1] == section['name']):
                self.tree.selection_set(item_id)
        
        if self.timer.sections:
            self.tree.insert('', 'end', values=(
                'TOT', 
                f"{len(self.timer.sections)}", 
                self.timer.format_time(self.timer.total_time), 
                ''
            ), tags=('total',))
            self.tree.tag_configure('total', background='lightgray', font=('Arial', 9, 'bold'))
    
    # MÈTODES GESTIÓ SECCIONS (TREE)
    def on_tree_select(self, event) -> None:
        """Gestiona la selecció d'elements del tree."""
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if column == '#4' and item:
            try:
                values = self.tree.item(item, 'values')
                if values and values[0] != 'TOT' and len(values) > 3 and values[3] == 'X':
                    index = int(values[0]) - 1
                    section_name = values[1]
                    if messagebox.askyesno("Eliminar", f'Eliminar "{section_name}"?'):
                        if self.timer.remove_section(index):
                            self.section_name_var.set(f"Secció {len(self.timer.sections) + 1}")
                    return
            except (tk.TclError, ValueError, IndexError):
                pass
        
        # Gestió del drag and drop
        if item:
            try:
                values = self.tree.item(item, 'values')
                if values and values[0] != 'TOT' and values[0].isdigit():
                    self.drag_data = {"item": item, "y": event.y, "dragging": False}
                    self.tree.selection_set(item)
                else:
                    self.drag_data = {"item": "", "y": 0, "dragging": False}
            except tk.TclError:
                self.drag_data = {"item": "", "y": 0, "dragging": False}
        else:
            self.drag_data = {"item": "", "y": 0, "dragging": False}

    def on_tree_drag(self, event) -> None:
        """Gestiona l'arrossegament d'elements."""
        if self.drag_data.get("item") and not self.drag_data.get("dragging"):
            if abs(event.y - self.drag_data["y"]) > 8:
                self.drag_data["dragging"] = True
                self.tree.configure(cursor="hand2")
                
                try:
                    if self.tree.exists(self.drag_data["item"]):
                        self.tree.selection_set(self.drag_data["item"])
                except tk.TclError:
                    pass

    def on_tree_drop(self, event) -> None:
        """Gestiona el drop d'elements."""
        self.tree.configure(cursor="")
        was_dragging = self.drag_data.get("dragging", False)
        source_item = self.drag_data.get("item", "")
        self.drag_data = {"item": "", "y": 0, "dragging": False}
        
        if not was_dragging or not source_item:
            return
            
        target_item = self.tree.identify_row(event.y)
        if not target_item:
            children = self.tree.get_children()
            if children:
                for child in children:
                    bbox = self.tree.bbox(child)
                    if bbox and bbox[1] <= event.y <= bbox[1] + bbox[3]:
                        target_item = child
                        break

        if not target_item or target_item == source_item:
            return
            
        try:
            source_values = self.tree.item(source_item, 'values')
            target_values = self.tree.item(target_item, 'values')
            
            if (source_values and target_values and 
                source_values[0] != 'TOT' and target_values[0] != 'TOT' and
                source_values[0].isdigit() and target_values[0].isdigit()):
                
                source_index = int(source_values[0]) - 1
                target_index = int(target_values[0]) - 1
                
                if 0 <= source_index < len(self.timer.sections) and 0 <= target_index < len(self.timer.sections):
                    section = self.timer.sections.pop(source_index)
                    self.timer.sections.insert(target_index, section)
                    
        except (tk.TclError, ValueError, IndexError):
            pass

    def on_double_click(self, event) -> None:
        """Gestiona el doble clic."""
        self.edit_section_name()

    def show_context_menu(self, event) -> None:
        """Mostra el menú contextual."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.tree.identify_row(event.y)
            if item:
                values = self.tree.item(item, 'values')
                if values and values[0] != 'TOT':
                    self.tree.selection_set(item)
                    self.context_menu.post(event.x_root, event.y_root)

    def delete_selected_section(self) -> None:
        """Elimina la secció seleccionada."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        if not values or values[0] == 'TOT':
            return
            
        index = int(values[0]) - 1
        section_name = values[1]
        
        if messagebox.askyesno("Eliminar", f'Eliminar "{section_name}"?'):
            if self.timer.remove_section(index):
                self.section_name_var.set(f"Secció {len(self.timer.sections) + 1}")

    def edit_section_name(self) -> None:
        """Edita el nom d'una secció."""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        values = self.tree.item(item, 'values')
        if not values or values[0] == 'TOT':
            return
            
        index = int(values[0]) - 1
        current_name = values[1]
        new_name = simpledialog.askstring(
            "Editar", 
            f"Nou nom secció {index + 1}:", 
            initialvalue=current_name, 
            parent=self.root
        )
        if new_name and new_name.strip():
            self.timer.sections[index]['name'] = new_name.strip()

    def edit_section_time(self) -> None:
        """Edita el temps d'una secció."""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        values = self.tree.item(item, 'values')
        if not values or values[0] == 'TOT':
            return
            
        index = int(values[0]) - 1
        current_duration = self.timer.sections[index]['duration']
        current_mins = current_duration // 60
        current_secs = current_duration % 60
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Editar Secció {index + 1}")
        edit_window.geometry("280x150")
        edit_window.transient(self.root)
        edit_window.grab_set()
        edit_window.resizable(False, False)
        
        frame = ttk.Frame(edit_window, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"{self.timer.sections[index]['name']}", 
                 font=('Arial', 10, 'bold')).pack(pady=(0, 5))
        ttk.Label(frame, text=f"Actual: {self.timer.format_time(current_duration)}").pack(pady=(0, 10))
        
        entry_frame = ttk.Frame(frame)
        entry_frame.pack(pady=5)
        
        min_var = tk.StringVar(value=str(current_mins))
        sec_var = tk.StringVar(value=str(current_secs))
        
        ttk.Label(entry_frame, text="Min:").grid(row=0, column=0, padx=(0, 5))
        min_entry = ttk.Entry(entry_frame, textvariable=min_var, width=8)
        min_entry.grid(row=0, column=1, padx=(0, 10))
        ttk.Label(entry_frame, text="Seg:").grid(row=0, column=2, padx=(0, 5))
        sec_entry = ttk.Entry(entry_frame, textvariable=sec_var, width=8)
        sec_entry.grid(row=0, column=3)
        
        def save_time():
            try:
                new_mins = int(min_var.get() or "0")
                new_secs = int(sec_var.get() or "0")
                if new_mins < 0 or new_secs < 0 or new_secs >= 60:
                    raise ValueError
                if new_mins == 0 and new_secs == 0:
                    raise ValueError
                    
                old_duration = self.timer.sections[index]['duration']
                new_duration = new_mins * 60 + new_secs
                self.timer.sections[index]['duration'] = new_duration
                self.timer.total_time = self.timer.total_time - old_duration + new_duration
                edit_window.destroy()
                messagebox.showinfo("OK", "Actualitzat!")
            except ValueError:
                messagebox.showerror("Error", "Valors incorrectes!")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Cancel·la", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="OK", command=save_time).pack(side=tk.LEFT)
        min_entry.focus()
        min_entry.select_range(0, tk.END)
    
    # MÈTODES REPRODUCTOR D'ÀUDIO
    def load_audio_files(self) -> None:
        """Carrega fitxers d'àudio."""
        if not PYGAME_AVAILABLE and not VLC_AVAILABLE:
            messagebox.showerror("Error", "Cap reproductor d'àudio disponible.")
            return
            
        file_types = [
            ("Fitxers d'àudio", "*.mp3 *.wav *.ogg"),
            ("MP3", "*.mp3"),
            ("WAV", "*.wav"),  
            ("OGG", "*.ogg"),
            ("Tots els fitxers", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Seleccionar fitxers d'àudio",
            filetypes=file_types
        )
        
        if files:
            added_files = self.audio_player.add_files(files)
            if added_files:
                self.update_audio_list()

    def toggle_play_pause(self) -> None:
        """Alterna entre play i pausa."""
        if not PYGAME_AVAILABLE and not VLC_AVAILABLE:
            messagebox.showerror("Error", "Cap reproductor d'àudio disponible.")
            return
            
        # Si no hi ha fitxer carregat, carrega el seleccionat
        if not self.audio_player.current_file:
            selection = self.audio_listbox.curselection()
            if not selection:
                messagebox.showwarning("Avís", "Selecciona un fitxer per reproduir.")
                return
            file_path = self.audio_player.files[selection[0]]
            if not self.audio_player.load_file(file_path):
                messagebox.showerror("Error", "No s'ha pogut carregar el fitxer.")
                return
            file_name = os.path.basename(file_path)
            if len(file_name) > 25:
                file_name = file_name[:22] + "..."
            self.current_audio_var.set(file_name)
        
        status = self.audio_player.get_status()
        
        if status == "playing":
            if self.audio_player.pause():
                self.play_pause_btn.configure(text="▶️")
        else:
            if self.audio_player.play():
                self.play_pause_btn.configure(text="⏸️")

    def stop_audio(self) -> None:
        """Para la reproducció d'àudio."""
        if PYGAME_AVAILABLE or VLC_AVAILABLE:
            self.audio_player.stop()
            self.current_audio_var.set("Cap fitxer seleccionat")
            self.audio_time_var.set("00:00 / --:--")
            self.audio_progress_var.set(0)
            self.play_pause_btn.configure(text="▶️")

    def change_volume(self, value) -> None:
        """Canvia el volum."""
        volume = float(value) / 100.0
        self.audio_player.set_volume(volume)

    def on_audio_double_click(self, event) -> None:
        """Gestiona el doble clic a la llista d'àudio."""
        selection = self.audio_listbox.curselection()
        if not selection:
            return
            
        file_path = self.audio_player.files[selection[0]]
        
        if self.audio_player.load_file(file_path):
            if self.audio_player.play():
                file_name = os.path.basename(file_path)
                if len(file_name) > 25:
                    file_name = file_name[:22] + "..."
                self.current_audio_var.set(file_name)
                self.play_pause_btn.configure(text="⏸️")

    def update_audio_list(self) -> None:
        """Actualitza la llista d'àudio."""
        self.audio_listbox.delete(0, tk.END)
        for file_path in self.audio_player.files:
            file_name = os.path.basename(file_path)
            self.audio_listbox.insert(tk.END, file_name)

    def update_audio_display(self) -> None:
        """Actualitza el display d'àudio."""
        if self.audio_player.use_vlc and self.audio_player.vlc_player:
            self._update_vlc_display()
        elif PYGAME_AVAILABLE:
            self._update_pygame_display()
        
        self.root.after(250, self.update_audio_display)
    
    def _update_vlc_display(self) -> None:
        """Actualitza display amb VLC."""
        status = self.audio_player.get_status()
        current_time = self.audio_player.get_current_time()
        
        if status == "playing" or status == "paused":
            minutes = int(current_time // 60)
            seconds = int(current_time % 60)
            
            try:
                duration_ms = self.audio_player.vlc_player.get_length()
                if duration_ms > 0:
                    duration = duration_ms / 1000.0
                    duration_min = int(duration // 60)
                    duration_sec = int(duration % 60)
                    
                    # Mostrar temps restant en lloc d'elapsed
                    remaining_time = duration - current_time
                    remaining_min = int(remaining_time // 60)
                    remaining_sec = int(remaining_time % 60)
                    
                    if status == "playing":
                        self.audio_time_var.set(f"-{remaining_min:02d}:{remaining_sec:02d} / {duration_min:02d}:{duration_sec:02d}")
                    else:  # paused
                        self.audio_time_var.set(f"-{remaining_min:02d}:{remaining_sec:02d} [PAUSA]")
                    
                    # Càlcul més precís del progrés (mantenim la precisió interna)
                    progress = min((current_time / duration) * 100, 100) if duration > 0 else 0
                    self.audio_progress_var.set(progress)
                else:
                    if status == "playing":
                        self.audio_time_var.set(f"{minutes:02d}:{seconds:02d} / --:--")
                    else:
                        self.audio_time_var.set(f"{minutes:02d}:{seconds:02d} [PAUSA]")
                    self.audio_progress_var.set(0)
            except Exception as e:
                if status == "playing":
                    self.audio_time_var.set(f"{minutes:02d}:{seconds:02d} / --:--")
                else:
                    self.audio_time_var.set(f"{minutes:02d}:{seconds:02d} [PAUSA]")
                self.audio_progress_var.set(0)
                
        elif status == "stopped":
            self.audio_time_var.set("00:00 / --:--")
            self.audio_progress_var.set(0)
    
    def _update_pygame_display(self) -> None:
        """Actualitza display amb Pygame."""
        status = self.audio_player.get_status()
        current_time = self.audio_player.get_current_time()
        
        if status == "playing":
            minutes = current_time // 60
            seconds = current_time % 60
            self.audio_time_var.set(f"{minutes:02d}:{seconds:02d} / --:--")
            
            max_time = 180
            progress = min((current_time / max_time) * 100, 100)
            self.audio_progress_var.set(progress)
            
        elif status == "paused":
            minutes = current_time // 60
            seconds = current_time % 60
            self.audio_time_var.set(f"{minutes:02d}:{seconds:02d} [PAUSA]")
            
        elif status == "stopped":
            self.audio_time_var.set("00:00 / --:--")
            self.audio_progress_var.set(0)

    def on_progress_click(self, event) -> None:
        """Gestiona el clic a la barra de progrés."""
        if not self.audio_player.current_file:
            return
            
        bar_width = self.audio_progress_bar.winfo_width()
        click_x = max(0, min(event.x, bar_width))
        click_position = click_x / bar_width if bar_width > 0 else 0
        
        if self.audio_player.use_vlc:
            if self.audio_player.set_position(click_position):
                self.audio_progress_var.set(click_position * 100)
            else:
                messagebox.showwarning("Error", "No s'ha pogut saltar a la posició")
        else:
            response = messagebox.askyesno(
                "Saltar en la reproducció", 
                f"Pygame només pot reiniciar. Vols reiniciar la cançó?",
                parent=self.root
            )
            if response:
                self.audio_player.stop()
                self.audio_player.play()

    def on_audio_drop(self, event) -> None:
        """Gestiona el drop de fitxers d'àudio."""
        files = []
        
        if hasattr(event, 'data'):
            data = event.data
            if isinstance(data, str):
                if data.startswith('{') and data.endswith('}'):
                    import re
                    files = re.findall(r'\{([^}]+)\}', data)
                else:
                    files = [data.strip()]
        
        audio_files = []
        for file_path in files:
            file_path = file_path.strip()
            if file_path.lower().endswith(('.mp3', '.wav', '.ogg')) and os.path.exists(file_path):
                audio_files.append(file_path)
        
        if audio_files:
            added_files = self.audio_player.add_files(audio_files)
            if added_files:
                self.update_audio_list()

    def show_audio_context_menu(self, event) -> None:
        """Mostra el menú contextual per àudio."""
        try:
            # Selecciona l'element on s'ha fet clic
            index = self.audio_listbox.nearest(event.y)
            
            if 0 <= index < self.audio_listbox.size():
                self.audio_listbox.selection_clear(0, tk.END)
                self.audio_listbox.selection_set(index)
                self.audio_listbox.activate(index)
                self.audio_context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error in show_audio_context_menu: {e}")

    def delete_selected_audio_file(self) -> None:
        """Elimina el fitxer d'àudio seleccionat."""
        selection = self.audio_listbox.curselection()
        if not selection:
            messagebox.showwarning("Avís", "Selecciona un fitxer per eliminar.")
            return
        
        index = selection[0]
        if 0 <= index < len(self.audio_player.files):
            file_path = self.audio_player.files[index]
            file_name = os.path.basename(file_path)
            
            if messagebox.askyesno("Eliminar fitxer", f'Eliminar "{file_name}" de la llista?'):
                if self.audio_player.remove_file(index):
                    self.update_audio_list()
                    # Si no hi ha més fitxers, reinicia l'estat
                    if not self.audio_player.files:
                        self.current_audio_var.set("Cap fitxer seleccionat")
                        self.audio_time_var.set("00:00 / --:--")
                        self.audio_progress_var.set(0)
                        self.play_pause_btn.configure(text="▶️")

    def play_selected_audio_file(self) -> None:
        """Reprodueix el fitxer d'àudio seleccionat."""
        selection = self.audio_listbox.curselection()
        if not selection:
            messagebox.showwarning("Avís", "Selecciona un fitxer per reproduir.")
            return
        
        index = selection[0]
        if 0 <= index < len(self.audio_player.files):
            file_path = self.audio_player.files[index]
            
            if self.audio_player.load_file(file_path):
                if self.audio_player.play():
                    file_name = os.path.basename(file_path)
                    if len(file_name) > 25:
                        file_name = file_name[:22] + "..."
                    self.current_audio_var.set(file_name)
                    self.play_pause_btn.configure(text="⏸️")
    
    # MÈTODES WHATSAPP I EXPORTAR
    def send_to_whatsapp(self, content: str) -> bool:
        """Envia contingut a WhatsApp."""
        whatsapp_content = self.format_for_whatsapp(content)
        encoded_message = urllib.parse.quote(whatsapp_content)
        url = f"https://web.whatsapp.com/send?text={encoded_message}"
        
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No s'ha pogut obrir WhatsApp: {e}")
            return False

    def format_for_whatsapp(self, content: str) -> str:
        """Formata contingut per WhatsApp."""
        lines = content.split('\n')
        whatsapp_content = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                whatsapp_content += "\n"
                continue
                
            if line.startswith("REGISTRE LA RENAIXENÇA"):
                whatsapp_content += f"📺 *{line}*\n"
            elif line.startswith("Data:"):
                whatsapp_content += f"📅 {line}\n"
            elif line.startswith("Hora:"):
                whatsapp_content += f"🕐 {line}\n"
            elif line.startswith("TOTAL:"):
                whatsapp_content += f"\n⏱️ *{line}*\n"
            elif line.startswith("Nº") and "|" in line:
                whatsapp_content += f"{line}\n"
            elif "|" in line and not line.startswith("-"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3 and parts[0].isdigit():
                    num = parts[0]
                    name = parts[1][:29].ljust(29)
                    duration = parts[2]
                    whatsapp_content += f"▶️{num} | {name} | *{duration}*\n"
            elif line.startswith("=") or line.startswith("-"):
                continue
            else:
                whatsapp_content += f"{line}\n"
        
        return whatsapp_content.strip()

    def export_sections(self) -> None:
        """Exporta les seccions."""
        if not self.timer.sections:
            messagebox.showwarning("Avís", "No hi ha seccions!")
            return
    
        content = self.timer.export_sections()
        
        export_window = tk.Toplevel(self.root)
        export_window.title("Exportar Seccions")
        export_window.geometry("600x500")
        export_window.transient(self.root)
        export_window.grab_set()
        
        text_frame = ttk.Frame(export_window, padding="10")
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        text_widget = tk.Text(text_frame, wrap=tk.NONE, font=('Courier New', 9))
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        text_widget.configure(yscrollcommand=v_scrollbar.set)
        
        text_widget.insert('1.0', content)
        text_widget.configure(state='disabled')
        
        button_frame = ttk.Frame(export_window)
        button_frame.grid(row=1, column=0, pady=10)
    
        def copy_only():
            self.root.clipboard_clear()
            self.root.clipboard_append(self.format_for_whatsapp(content))
            messagebox.showinfo("OK", "Registre copiat al portapapers!")
    
        def copy_and_browser():
            self.root.clipboard_clear()
            self.root.clipboard_append(self.format_for_whatsapp(content))
            if self.send_to_whatsapp(content):
                messagebox.showinfo("OK", "Text copiat al portapapers!\nWhatsApp Web obert al navegador.\nEnganxa amb Ctrl+V")
                export_window.destroy()
            else:
                messagebox.showinfo("OK", "Text copiat al portapapers!")
        
        ttk.Button(button_frame, text="Copiar", command=copy_only).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Copiar i obrir WhatsApp Web", command=copy_and_browser).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Tancar", command=export_window.destroy).pack(side=tk.LEFT, padx=10)
        
        export_window.columnconfigure(0, weight=1)
        export_window.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
    
    # MÈTODES FUNCIONALITAT PRESIDENTS
    def mark_president_correct(self) -> None:
        """Marca el president com a correcte."""
        if self.presidents_game.mark_correct():
            self.update_presidents_display()
            if self.presidents_game.is_completed():
                messagebox.showinfo("Felicitats!", f"Tots els {len(self.presidents_game.presidents)} presidents completats!")

    def reset_presidents_game(self) -> None:
        """Reinicia el joc de presidents."""
        if messagebox.askyesno("Reiniciar Presidents", "Reiniciar el joc de presidents?"):
            self.presidents_game.reset_game()
            self.update_presidents_display()

    def update_presidents_display(self) -> None:
        """Actualitza el display de presidents."""
        self.presidents_progress_var.set(self.presidents_game.get_progress())
        current = self.presidents_game.get_current_president()
        self.current_president_var.set(current)
        
        if self.presidents_game.is_completed():
            self.current_president_label.configure(foreground='green')
            self.correct_btn.configure(state='disabled', text="Completat")
        else:
            self.current_president_label.configure(foreground='black')
            self.correct_btn.configure(state='normal', text="Correcte")
        
        self.completed_text.configure(state='normal')
        self.completed_text.delete('1.0', tk.END)
        if self.presidents_game.completed:
            for i, president in enumerate(self.presidents_game.completed, 1):
                name_only = president.split(' (')[0]
                self.completed_text.insert(tk.END, f"{i}. {name_only}\n")
        else:
            self.completed_text.insert(tk.END, "Cap president completat encara.")
        self.completed_text.configure(state='disabled')
        self.completed_text.see(tk.END)

    def export_presidents_record(self) -> None:
        """Exporta el registre de presidents."""
        if not self.presidents_game.completed:
            messagebox.showwarning("Avís", "No hi ha presidents completats!")
            return
        
        now = datetime.now()
        guest_name = self.guest_name_var.get().strip() or "Convidat"
        content = f"REGISTRE PRESIDENTS GENERALITAT - PROGRAMA #{self.timer.program_number}\n"
        content += "=" * 60 + "\n"
        content += f"Convidat: {guest_name}\n"
        content += f"Data: {self.timer.get_catalan_date()}\n"
        content += f"Hora: {now.strftime('%H:%M:%S')}\n\n"
        content += f"Presidents encertats: {len(self.presidents_game.completed)} de {len(self.presidents_game.presidents)}\n"
        content += "-" * 60 + "\n"
        for i, president in enumerate(self.presidents_game.completed, 1):
            content += f"{i:2d}. {president}\n"
        content += "-" * 60 + "\n"
        content += f"Percentatge d'encert: {(len(self.presidents_game.completed)/len(self.presidents_game.presidents)*100):.1f}%\n"
        
        export_window = tk.Toplevel(self.root)
        export_window.title("Registre Presidents")
        export_window.geometry("800x600")
        export_window.transient(self.root)
        export_window.grab_set()
        
        text_frame = ttk.Frame(export_window, padding="10")
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(text_frame, text="Registre de Presidents", font=('Arial', 12, 'bold')).grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        text_container = ttk.Frame(text_frame)
        text_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_container.columnconfigure(0, weight=1)
        text_container.rowconfigure(0, weight=1)
        
        text_widget = tk.Text(text_container, wrap=tk.NONE, font=('Courier New', 9))
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        v_scrollbar = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=text_widget.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        text_widget.configure(yscrollcommand=v_scrollbar.set)
        
        text_widget.insert('1.0', content)
        text_widget.configure(state='disabled')
        
        button_frame = ttk.Frame(text_frame)
        button_frame.grid(row=2, column=0, pady=(15, 0))
        
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("OK", "Registre copiat al portapapers!")
        
        ttk.Button(button_frame, text="Copiar", command=copy_to_clipboard).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Tancar", command=export_window.destroy).pack(side=tk.LEFT, padx=10)
        
        export_window.columnconfigure(0, weight=1)
        export_window.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(1, weight=1)


def main():
    """Funció principal."""
    if DRAG_DROP_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    app = TimerApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nAplicació tancada")
        sys.exit(0)


if __name__ == "__main__":
    main()
