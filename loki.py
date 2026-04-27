#!/usr/bin/env python3
"""

"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import time
import socket
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
import re

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

VERSION = "2.0.0"
APP_NAME = "LOKI Network Toolkit"
APP_CODENAME = "Mjölnir"
AUTHOR = "Catarina"
GITHUB_REPO = "https://github.com/catarina/loki"

# Cores do tema (Magenta + Cinza)
COLORS = {
    'bg_dark': '#0a0a0a',
    'bg_medium': '#1a1a2e',
    'bg_light': '#2d2d2d',
    'accent': '#ff00ff',
    'accent_light': '#ff66cc',
    'success': '#00ff00',
    'warning': '#ff6600',
    'error': '#ff0000',
    'text': '#e0e0e0',
    'text_dim': '#888888'
}

# ============================================================================
# CLASSES
# ============================================================================

class NetworkScanner:
    """Scanner de rede para descoberta de dispositivos"""
    
    @staticmethod
    def get_gateway() -> str:
        """Obtém o gateway padrão da rede"""
        try:
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'Default Gateway' in line and ':' in line:
                    gateway = line.split(':')[-1].strip()
                    if gateway and not gateway.startswith('0.0.0.0'):
                        return gateway
        except:
            pass
        return "192.168.1.1"
    
    @staticmethod
    def get_network(gateway: str) -> str:
        """Obtém a rede a partir do gateway"""
        parts = gateway.split('.')
        if len(parts) == 4:
            return '.'.join(parts[:3]) + '.'
        return "192.168.1."
    
    @staticmethod
    def scan(ip_range: str, callback=None) -> List[Dict]:
        """Escaneia a rede em busca de dispositivos"""
        devices = []
        
        for i in range(1, 255):
            ip = f"{ip_range}{i}"
            result = subprocess.run(['ping', '-n', '1', '-w', '100', ip], 
                                   capture_output=True, text=True)
            
            if callback:
                callback(i)
            
            if 'Resposta' in result.stdout or 'Reply' in result.stdout:
                hostname = NetworkScanner.get_hostname(ip)
                mac = NetworkScanner.get_mac(ip)
                devices.append({
                    'ip': ip,
                    'mac': mac,
                    'hostname': hostname,
                    'status': 'active'
                })
        
        return devices
    
    @staticmethod
    def get_hostname(ip: str) -> str:
        """Tenta obter o hostname do dispositivo"""
        try:
            return socket.gethostbyaddr(ip)[0].split('.')[0]
        except:
            return ip
    
    @staticmethod
    def get_mac(ip: str) -> str:
        """Tenta obter o MAC address do dispositivo"""
        try:
            result = subprocess.run(['arp', '-a', ip], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if ip in line:
                    parts = line.split()
                    if len(parts) >= 2 and ':' in parts[1]:
                        return parts[1]
        except:
            pass
        return "??:??:??:??:??:??"


class FirewallController:
    """Controlador do Firewall do Windows"""
    
    @staticmethod
    def block_ip(ip: str) -> bool:
        """Bloqueia um IP no firewall"""
        rule_name = f"LOKI_BLOCK_{ip.replace('.', '_')}"
        result = subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
            f'name={rule_name}', 'dir=out', 'action=block',
            f'remoteip={ip}', 'protocol=any'
        ], capture_output=True)
        return result.returncode == 0
    
    @staticmethod
    def unblock_ip(ip: str) -> bool:
        """Desbloqueia um IP no firewall"""
        rule_name = f"LOKI_BLOCK_{ip.replace('.', '_')}"
        result = subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'delete', 'rule', f'name={rule_name}'
        ], capture_output=True)
        return result.returncode == 0
    
    @staticmethod
    def apocalypse() -> None:
        """Bloqueia todo o tráfego de rede"""
        subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
            'name="LOKI_APOCALYPSE"', 'dir=out', 'action=block',
            'protocol=any', 'remoteip=any'
        ], capture_output=True)
    
    @staticmethod
    def restore() -> None:
        """Restaura o tráfego de rede"""
        subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name="LOKI_APOCALYPSE"'
        ], capture_output=True)


class LokiApp:
    """Aplicação principal do LOKI"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"🐍 {APP_NAME} v{VERSION} - {APP_CODENAME}")
        self.root.geometry("1300x800")
        self.root.minsize(1000, 600)
        self.root.configure(bg=COLORS['bg_dark'])
        
        # Configurar ícone (opcional)
        try:
            self.root.iconbitmap('loki.ico')
        except:
            pass
        
        # Estado da aplicação
        self.devices: List[Dict] = []
        self.selected_ip: Optional[str] = None
        self.selected_mac: Optional[str] = None
        self.lag_active = False
        self.stealth_mode = False
        self.scanning = False
        self.network: Optional[str] = None
        self.gateway: str = NetworkScanner.get_gateway()
        
        self._setup_ui()
        self._log(f"🐍 {APP_NAME} v{VERSION} iniciado")
        self._log(f"🌐 Gateway: {self.gateway}")
        self._log(f" Rede: {NetworkScanner.get_network(self.gateway)}0/24")
        self._log(f" Executando como: {'Administrador' if self._is_admin() else 'Usuário'}")
        
    def _is_admin(self) -> bool:
        """Verifica se o programa está rodando como administrador"""
        try:
            return os.getuid() == 0
        except AttributeError:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    def _setup_ui(self):
        """Configura a interface gráfica"""
        # ========== HEADER ==========
        header = tk.Frame(self.root, bg=COLORS['bg_light'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Logo e título
        title_frame = tk.Frame(header, bg=COLORS['bg_light'])
        title_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(title_frame, text="🐍 LOKI", font=('Arial', 28, 'bold'),
                bg=COLORS['bg_light'], fg=COLORS['accent']).pack(side=tk.LEFT)
        
        tk.Label(title_frame, text=f" v{VERSION}", font=('Arial', 14),
                bg=COLORS['bg_light'], fg=COLORS['text_dim']).pack(side=tk.LEFT)
        
        tk.Label(title_frame, text=f" - {APP_CODENAME}", font=('Arial', 12),
                bg=COLORS['bg_light'], fg=COLORS['warning']).pack(side=tk.LEFT, padx=10)
        
        # Status
        self.status_label = tk.Label(header, text="● PARADO", font=('Arial', 11, 'bold'),
                                     bg=COLORS['bg_light'], fg=COLORS['error'])
        self.status_label.pack(side=tk.LEFT, padx=30)
        
        # Modo stealth
        self.stealth_btn = tk.Button(header, text="👻 STEALTH: OFF", command=self._toggle_stealth,
                                     bg=COLORS['bg_dark'], fg=COLORS['text'], 
                                     font=('Arial', 10, 'bold'), relief=tk.FLAT)
        self.stealth_btn.pack(side=tk.RIGHT, padx=20)
        
        # Gateway info
        tk.Label(header, text=f" Gateway: {self.gateway}", font=('Arial', 10),
                bg=COLORS['bg_light'], fg=COLORS['text_dim']).pack(side=tk.RIGHT, padx=20)
        
        # ========== MAIN CONTENT ==========
        main = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Notebook (abas)
        notebook = ttk.Notebook(main)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Configurar estilo do notebook
        style = ttk.Style()
        style.configure('TNotebook', background=COLORS['bg_dark'])
        style.configure('TNotebook.Tab', background=COLORS['bg_medium'], 
                       padding=[10, 5], font=('Arial', 10))
        
        # Abas
        self._create_dashboard_tab(notebook)
        self._create_network_tab(notebook)
        self._create_firewall_tab(notebook)
        self._create_scanner_tab(notebook)
        self._create_apocalypse_tab(notebook)
        self._create_log_tab(notebook)
        
        # Auto-scan após 2 segundos
        self.root.after(2000, self.scan_network)
    
    def _create_dashboard_tab(self, notebook):
        """Cria a aba de dashboard"""
        frame = tk.Frame(notebook, bg=COLORS['bg_dark'])
        notebook.add(frame, text=" DASHBOARD")
        
        # Stats cards
        stats_frame = tk.Frame(frame, bg=COLORS['bg_dark'])
        stats_frame.pack(fill=tk.X, pady=20, padx=20)
        
        cards = [
            (" DISPOSITIVOS", "0", COLORS['accent']),
            ("⚠️ ALERTAS", "0", COLORS['warning']),
            (" BLOQUEADOS", "0", COLORS['success']),
            ("⏱️ UPTIME", "0h", COLORS['text_dim'])
        ]
        
        self.stats_vars = {}
        for i, (title, value, color) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=COLORS['bg_medium'], relief=tk.RAISED, bd=1)
            card.grid(row=0, column=i, padx=10, ipadx=20, ipady=15, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
            
            tk.Label(card, text=title, font=('Arial', 10), 
                    bg=COLORS['bg_medium'], fg=color).pack()
            var = tk.StringVar(value=value)
            self.stats_vars[title] = var
            tk.Label(card, textvariable=var, font=('Arial', 24, 'bold'),
                    bg=COLORS['bg_medium'], fg=COLORS['text']).pack()
        
        # Informações
        info_frame = tk.LabelFrame(frame, text="ℹ️ INFORMAÇÕES DO SISTEMA", 
                                   font=('Arial', 11, 'bold'),
                                   bg=COLORS['bg_medium'], fg=COLORS['accent'])
        info_frame.pack(fill=tk.X, padx=20, pady=20)
        
        info_text = tk.Text(info_frame, height=10, bg=COLORS['bg_dark'], 
                           fg=COLORS['text'], font=('Courier', 9), wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_text.insert(tk.END, f" SO: Windows\n")
        info_text.insert(tk.END, f"🐍 Python: {sys.version.split()[0]}\n")
        info_text.insert(tk.END, f" Gateway: {self.gateway}\n")
        info_text.insert(tk.END, f" Rede: {NetworkScanner.get_network(self.gateway)}0/24\n")
        info_text.insert(tk.END, f" Admin: {'Sim' if self._is_admin() else 'Não (funcionalidade limitada)'}\n")
        info_text.config(state=tk.DISABLED)
    
    def _create_network_tab(self, notebook):
        """Cria a aba de rede (dispositivos)"""
        frame = tk.Frame(notebook, bg=COLORS['bg_dark'])
        notebook.add(frame, text="📡 REDE")
        
        # Lista de dispositivos
        list_frame = tk.LabelFrame(frame, text=" DISPOSITIVOS NA REDE",
                                   font=('Arial', 11, 'bold'),
                                   bg=COLORS['bg_medium'], fg=COLORS['accent'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        list_container = tk.Frame(list_frame, bg=COLORS['bg_medium'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scroll = tk.Scrollbar(list_container)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.devices_listbox = tk.Listbox(list_container, bg=COLORS['bg_dark'], 
                                          fg=COLORS['text'], font=('Courier', 10),
                                          selectbackground=COLORS['accent'],
                                          yscrollcommand=scroll.set, height=20)
        self.devices_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.devices_listbox.yview)
        self.devices_listbox.bind('<<ListboxSelect>>', self._on_device_select)
        
        # Botões
        btn_frame = tk.Frame(frame, bg=COLORS['bg_dark'])
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.scan_btn = tk.Button(btn_frame, text="🔍 ESCANEAR REDE", command=self.scan_network,
                                  bg=COLORS['accent'], fg=COLORS['bg_dark'], 
                                  font=('Arial', 10, 'bold'), padx=15, pady=5)
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.block_btn = tk.Button(btn_frame, text=" BLOQUEAR SELECIONADO", 
                                   command=self._block_selected,
                                   bg=COLORS['error'], fg='white', 
                                   font=('Arial', 10, 'bold'), padx=15, pady=5,
                                   state=tk.DISABLED)
        self.block_btn.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(btn_frame, length=300, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=20)
    
    def _create_firewall_tab(self, notebook):
        """Cria a aba de firewall"""
        frame = tk.Frame(notebook, bg=COLORS['bg_dark'])
        notebook.add(frame, text="🛡️ FIREWALL")
        
        # Bloqueio manual
        manual_frame = tk.LabelFrame(frame, text=" BLOQUEIO MANUAL",
                                     font=('Arial', 11, 'bold'),
                                     bg=COLORS['bg_medium'], fg=COLORS['accent'])
        manual_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ip_frame = tk.Frame(manual_frame, bg=COLORS['bg_medium'])
        ip_frame.pack(pady=20)
        
        tk.Label(ip_frame, text="IP:", font=('Arial', 11), 
                bg=COLORS['bg_medium'], fg=COLORS['text']).pack(side=tk.LEFT, padx=10)
        self.manual_ip = tk.Entry(ip_frame, width=20, font=('Arial', 11),
                                  bg=COLORS['bg_dark'], fg=COLORS['text'])
        self.manual_ip.pack(side=tk.LEFT, padx=10)
        
        tk.Button(ip_frame, text=" BLOQUEAR", command=self._manual_block,
                  bg=COLORS['error'], fg='white', font=('Arial', 10, 'bold'), 
                  padx=15, pady=5).pack(side=tk.LEFT, padx=10)
        
        tk.Button(ip_frame, text=" DESBLOQUEAR", command=self._manual_unblock,
                  bg=COLORS['success'], fg=COLORS['bg_dark'], font=('Arial', 10, 'bold'), 
                  padx=15, pady=5).pack(side=tk.LEFT, padx=10)
        
        # Lista de bloqueados
        blocked_frame = tk.LabelFrame(frame, text=" IPS BLOQUEADOS",
                                      font=('Arial', 11, 'bold'),
                                      bg=COLORS['bg_medium'], fg=COLORS['error'])
        blocked_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.blocked_listbox = tk.Listbox(blocked_frame, bg=COLORS['bg_dark'], 
                                          fg=COLORS['error'], font=('Courier', 10),
                                          height=10)
        self.blocked_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _create_scanner_tab(self, notebook):
        """Cria a aba de scanner de vulnerabilidades"""
        frame = tk.Frame(notebook, bg=COLORS['bg_dark'])
        notebook.add(frame, text="🔍 SCANNER")
        
        btn_frame = tk.Frame(frame, bg=COLORS['bg_dark'])
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="🔍 SCANEAR PORTAS", command=self._scan_ports,
                  bg=COLORS['accent'], fg=COLORS['bg_dark'], font=('Arial', 10, 'bold'),
                  padx=15, pady=5).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text=" SCANEAR REDE", command=self.scan_network,
                  bg=COLORS['warning'], fg=COLORS['bg_dark'], font=('Arial', 10, 'bold'),
                  padx=15, pady=5).pack(side=tk.LEFT, padx=10)
        
        self.scan_result = scrolledtext.ScrolledText(frame, bg=COLORS['bg_dark'],
                                                     fg=COLORS['text'], font=('Courier', 9))
        self.scan_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _create_apocalypse_tab(self, notebook):
        """Cria a aba de apocalipse"""
        frame = tk.Frame(notebook, bg=COLORS['bg_dark'])
        notebook.add(frame, text=" APOCALIPSE")
        
        # Aviso
        warning = tk.Label(frame, text="  ISSO VAI DERRUBAR SUA INTERNET!  ",
                          font=('Arial', 16, 'bold'), bg=COLORS['bg_dark'], fg=COLORS['error'])
        warning.pack(pady=30)
        
        tk.Label(frame, text="Clique apenas se você realmente quer derrubar toda a conexão de rede",
                bg=COLORS['bg_dark'], fg=COLORS['text_dim']).pack()
        
        btn_frame = tk.Frame(frame, bg=COLORS['bg_dark'])
        btn_frame.pack(pady=40)
        
        self.apoc_btn = tk.Button(btn_frame, text="💀 ATIVAR APOCALIPSE", command=self._apocalypse,
                                  bg=COLORS['error'], fg='white', font=('Arial', 14, 'bold'),
                                  padx=40, pady=15)
        self.apoc_btn.pack(side=tk.LEFT, padx=20)
        
        self.restore_btn = tk.Button(btn_frame, text=" RESTAURAR INTERNET", command=self._restore,
                                     bg=COLORS['success'], fg=COLORS['bg_dark'], 
                                     font=('Arial', 14, 'bold'), padx=40, pady=15)
        self.restore_btn.pack(side=tk.LEFT, padx=20)
        
        tk.Label(frame, text="💡 O modo Apocalipse bloqueia todo o tráfego de rede do seu computador.\n"
                           "Clique em 'RESTAURAR' para voltar ao normal.",
                bg=COLORS['bg_dark'], fg=COLORS['text_dim'], justify=tk.CENTER).pack(pady=20)
    
    def _create_log_tab(self, notebook):
        """Cria a aba de log"""
        frame = tk.Frame(notebook, bg=COLORS['bg_dark'])
        notebook.add(frame, text=" LOG")
        
        self.log_area = scrolledtext.ScrolledText(frame, bg=COLORS['bg_dark'],
                                                  fg=COLORS['text'], font=('Courier', 9))
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra de botões do log
        log_btn_frame = tk.Frame(frame, bg=COLORS['bg_dark'])
        log_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(log_btn_frame, text=" LIMPAR LOG", command=self._clear_log,
                  bg=COLORS['bg_medium'], fg=COLORS['text'], font=('Arial', 9),
                  padx=10, pady=3).pack(side=tk.LEFT, padx=5)
        
        tk.Button(log_btn_frame, text=" COPIAR LOG", command=self._copy_log,
                  bg=COLORS['bg_medium'], fg=COLORS['text'], font=('Arial', 9),
                  padx=10, pady=3).pack(side=tk.LEFT, padx=5)
    
    # ========================================================================
    # MÉTODOS PRINCIPAIS
    # ========================================================================
    
    def _log(self, message: str):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        try:
            self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_area.see(tk.END)
        except:
            print(f"[{timestamp}] {message}")
    
    def _clear_log(self):
        """Limpa o log"""
        self.log_area.delete(1.0, tk.END)
        self._log("Log limpo")
    
    def _copy_log(self):
        """Copia o log para a área de transferência"""
        log_content = self.log_area.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(log_content)
        self._log("Log copiado para área de transferência")
    
    def _toggle_stealth(self):
        """Ativa/desativa o modo stealth"""
        self.stealth_mode = not self.stealth_mode
        if self.stealth_mode:
            self.stealth_btn.config(text="👻 STEALTH: ON", bg=COLORS['success'])
            self.root.title("System Idle Process")
            self._log("👻 Modo stealth ativado - Janela camuflada")
        else:
            self.stealth_btn.config(text="👻 STEALTH: OFF", bg=COLORS['bg_dark'])
            self.root.title(f"🐍 {APP_NAME} v{VERSION}")
            self._log("👻 Modo stealth desativado")
    
    def _on_device_select(self, event):
        """Handler para seleção de dispositivo na lista"""
        selection = self.devices_listbox.curselection()
        if selection:
            idx = selection[0]
            if idx < len(self.devices):
                device = self.devices[idx]
                self.selected_ip = device['ip']
                self.selected_mac = device.get('mac', '??:??:??:??:??:??')
                self.block_btn.config(state=tk.NORMAL)
                self.manual_ip.delete(0, tk.END)
                self.manual_ip.insert(0, self.selected_ip)
                self._log(f"🎯 Selecionado: {device.get('hostname', self.selected_ip)} ({self.selected_ip})")
    
    def _manual_block(self):
        """Bloqueia IP manualmente"""
        ip = self.manual_ip.get().strip()
        if not ip:
            self._log("❌ Digite um IP válido")
            return
        
        if FirewallController.block_ip(ip):
            self._log(f"🚫 IP {ip} BLOQUEADO com sucesso")
            self.status_label.config(text=f"● BLOQUEADO: {ip}", fg=COLORS['error'])
            self.blocked_listbox.insert(tk.END, ip)
        else:
            self._log(f"❌ Falha ao bloquear {ip}")
    
    def _manual_unblock(self):
        """Desbloqueia IP manualmente"""
        ip = self.manual_ip.get().strip()
        if not ip:
            self._log("❌ Digite um IP válido")
            return
        
        if FirewallController.unblock_ip(ip):
            self._log(f"✅ IP {ip} DESBLOQUEADO")
            self.status_label.config(text="● PARADO", fg=COLORS['error'])
            # Remover da lista
            items = self.blocked_listbox.get(0, tk.END)
            for i, item in enumerate(items):
                if ip in item:
                    self.blocked_listbox.delete(i)
                    break
        else:
            self._log(f"❌ Falha ao desbloquear {ip}")
    
    def _block_selected(self):
        """Bloqueia o dispositivo selecionado"""
        if self.selected_ip:
            if FirewallController.block_ip(self.selected_ip):
                self._log(f"🚫 Dispositivo {self.selected_ip} BLOQUEADO")
                self.status_label.config(text=f"● BLOQUEADO: {self.selected_ip}", fg=COLORS['error'])
                self.blocked_listbox.insert(tk.END, self.selected_ip)
            else:
                self._log(f"❌ Falha ao bloquear {self.selected_ip}")
    
    def _apocalypse(self):
        """Ativa o modo apocalipse"""
        if messagebox.askyesno("⚠️ APOCALIPSE", 
                               "Isso vai derrubar toda a sua internet!\n\n"
                               "Tem certeza que deseja continuar?"):
            FirewallController.apocalypse()
            self._log("💀💀💀 MODO APOCALIPSE ATIVADO 💀💀💀")
            self._log("🌐 Sua internet foi derrubada!")
            self.status_label.config(text="● APOCALIPSE", fg=COLORS['error'])
            self.apoc_btn.config(state=tk.DISABLED)
    
    def _restore(self):
        """Restaura a internet"""
        FirewallController.restore()
        self._log(" Internet restaurada!")
        self.status_label.config(text="● PARADO", fg=COLORS['error'])
        self.apoc_btn.config(state=tk.NORMAL)
    
    def _scan_ports(self):
        """Escaneia portas do dispositivo selecionado"""
        if not self.selected_ip:
            self._log("❌ Selecione um dispositivo primeiro")
            return
        
        self.scan_result.delete(1.0, tk.END)
        self.scan_result.insert(tk.END, f"🔍 Escaneando {self.selected_ip}...\n\n")
        
        def scan():
            portas = [21, 22, 23, 80, 443, 445, 8080, 8443, 3306, 3389, 5900]
            abertas = []
            
            for porta in portas:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    result = sock.connect_ex((self.selected_ip, porta))
                    sock.close()
                    
                    if result == 0:
                        abertas.append(porta)
                        self.scan_result.insert(tk.END, f"✅ Porta {porta} - ABERTA\n")
                    else:
                        self.scan_result.insert(tk.END, f"❌ Porta {porta} - FECHADA\n")
                except:
                    pass
                
                self.scan_result.see(tk.END)
                self.root.update()
            
            if abertas:
                self._log(f"🔍 Portas abertas em {self.selected_ip}: {abertas}")
            else:
                self._log(f"🔍 Nenhuma porta comum aberta em {self.selected_ip}")
        
        threading.Thread(target=scan, daemon=True).start()
    
    def scan_network(self):
        """Escaneia a rede em busca de dispositivos"""
        if self.scanning:
            self._log("⚠️ Escaneamento já em andamento")
            return
        
        self.scanning = True
        self.scan_btn.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.devices_listbox.delete(0, tk.END)
        self.devices = []
        
        network = NetworkScanner.get_network(self.gateway)
        self._log(f"🔍 Escaneando rede {network}0/24...")
        
        def update_progress(i):
            self.progress_bar['value'] = i
            self.root.update()
        
        def scan():
            devices = NetworkScanner.scan(network, update_progress)
            self.devices = devices
            
            for device in devices:
                hostname = device.get('hostname', device['ip'])
                mac = device.get('mac', '??:??:??:??:??:??')
                self.devices_listbox.insert(tk.END, f"📱 {hostname[:20]} - {device['ip']} - {mac}")
                self._log(f"   ✅ {hostname} ({device['ip']})")
            
            self.scanning = False
            self.scan_btn.config(state=tk.NORMAL)
            self._log(f"✅ Escaneamento concluído! {len(devices)} dispositivos encontrados.")
            
            if self.stats_vars:
                self.stats_vars["🖥️ DISPOSITIVOS"].set(str(len(devices)))
        
        threading.Thread(target=scan, daemon=True).start()


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Função principal"""
    root = tk.Tk()
    app = LokiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()