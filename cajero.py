import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk
import hashlib

class CajeroAutomatico:
    def __init__(self, root):
        self.root = root
        self.root.title("Cajero Automático - Banco SENA")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e293b")
        
        # Variables
        self.usuario_actual = None
        self.cuenta_actual = None
        
        # Inicializar base de datos
        self.init_database()
        
        # Mostrar pantalla de login
        self.mostrar_login()
    
    def init_database(self):
        """Inicializa la base de datos SQLite"""
        self.conn = sqlite3.connect('cajero.db')
        self.cursor = self.conn.cursor()
        
        # Tabla de usuarios
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_cuenta TEXT UNIQUE NOT NULL,
                pin TEXT NOT NULL,
                nombre TEXT NOT NULL,
                saldo REAL DEFAULT 0,
                fecha_creacion TEXT
            )
        ''')
        
        # Tabla de transacciones
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_cuenta TEXT,
                tipo TEXT,
                monto REAL,
                saldo_anterior REAL,
                saldo_nuevo REAL,
                fecha TEXT,
                FOREIGN KEY (numero_cuenta) REFERENCES usuarios(numero_cuenta)
            )
        ''')
        
        # Crear cuenta de prueba si no existe
        self.cursor.execute("SELECT * FROM usuarios WHERE numero_cuenta = ?", ("1234567890",))
        if not self.cursor.fetchone():
            pin_hash = hashlib.sha256("1234".encode()).hexdigest()
            self.cursor.execute('''
                INSERT INTO usuarios (numero_cuenta, pin, nombre, saldo, fecha_creacion)
                VALUES (?, ?, ?, ?, ?)
            ''', ("1234567890", pin_hash, "Mairon Salazar", 5000000, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        self.conn.commit()
    
    def limpiar_ventana(self):
        """Limpia todos los widgets de la ventana"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def mostrar_login(self):
        """Muestra la pantalla de inicio de sesión"""
        self.limpiar_ventana()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#1e293b")
        main_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        # Título
        titulo = tk.Label(
            main_frame,
            text="🏦 CAJERO AUTOMÁTICO",
            font=("Arial", 32, "bold"),
            bg="#1e293b",
            fg="#667eea"
        )
        titulo.pack(pady=30)
        
        # Subtítulo
        subtitulo = tk.Label(
            main_frame,
            text="Banco SENA - Bienvenido",
            font=("Arial", 16),
            bg="#1e293b",
            fg="#cbd5e1"
        )
        subtitulo.pack(pady=10)
        
        # Frame del formulario
        form_frame = tk.Frame(main_frame, bg="#334155", relief="raised", bd=2)
        form_frame.pack(pady=30, padx=100, fill="x")
        
        # Número de cuenta
        tk.Label(
            form_frame,
            text="Número de Cuenta:",
            font=("Arial", 14),
            bg="#334155",
            fg="white"
        ).pack(pady=(20, 5))
        
        self.entry_cuenta = tk.Entry(
            form_frame,
            font=("Arial", 14),
            width=25,
            justify="center"
        )
        self.entry_cuenta.pack(pady=5)
        self.entry_cuenta.insert(0, "1234567890")  # Valor por defecto para prueba
        
        # PIN
        tk.Label(
            form_frame,
            text="PIN:",
            font=("Arial", 14),
            bg="#334155",
            fg="white"
        ).pack(pady=(15, 5))
        
        self.entry_pin = tk.Entry(
            form_frame,
            font=("Arial", 14),
            width=25,
            show="●",
            justify="center"
        )
        self.entry_pin.pack(pady=5)
        self.entry_pin.insert(0, "1234")  # Valor por defecto para prueba
        
        # Botón de ingreso
        btn_ingresar = tk.Button(
            form_frame,
            text="INGRESAR",
            font=("Arial", 14, "bold"),
            bg="#667eea",
            fg="white",
            width=20,
            height=2,
            cursor="hand2",
            command=self.iniciar_sesion
        )
        btn_ingresar.pack(pady=30)
        
        # Información de prueba
        info = tk.Label(
            main_frame,
            text="Cuenta de prueba: 1234567890 | PIN: 1234",
            font=("Arial", 10, "italic"),
            bg="#1e293b",
            fg="#94a3b8"
        )
        info.pack(pady=10)
        
        # Bind Enter key
        self.entry_pin.bind('<Return>', lambda e: self.iniciar_sesion())
    
    def iniciar_sesion(self):
        """Valida las credenciales e inicia sesión"""
        numero_cuenta = self.entry_cuenta.get()
        pin = self.entry_pin.get()
        
        if not numero_cuenta or not pin:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        self.cursor.execute('''
            SELECT * FROM usuarios WHERE numero_cuenta = ? AND pin = ?
        ''', (numero_cuenta, pin_hash))
        
        usuario = self.cursor.fetchone()
        
        if usuario:
            self.usuario_actual = {
                'id': usuario[0],
                'numero_cuenta': usuario[1],
                'nombre': usuario[3],
                'saldo': usuario[4]
            }
            self.mostrar_menu_principal()
        else:
            messagebox.showerror("Error", "Número de cuenta o PIN incorrecto")
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal del cajero"""
        self.limpiar_ventana()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#1e293b")
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Header
        header = tk.Frame(main_frame, bg="#334155")
        header.pack(fill="x", pady=(0, 30))
        
        tk.Label(
            header,
            text=f"Bienvenido, {self.usuario_actual['nombre']}",
            font=("Arial", 20, "bold"),
            bg="#334155",
            fg="white"
        ).pack(pady=15)
        
        tk.Label(
            header,
            text=f"Cuenta: {self.usuario_actual['numero_cuenta']}",
            font=("Arial", 12),
            bg="#334155",
            fg="#cbd5e1"
        ).pack(pady=(0, 15))
        
        # Grid de botones
        botones_frame = tk.Frame(main_frame, bg="#1e293b")
        botones_frame.pack(expand=True)
        
        botones = [
            (" Consultar Saldo", self.consultar_saldo),
            (" Retirar Dinero", self.retirar_dinero),
            (" Depositar Dinero", self.depositar_dinero),
            (" Transferir", self.transferir),
            (" Ver Movimientos", self.ver_movimientos),
            (" Salir", self.cerrar_sesion)
        ]
        
        for i, (texto, comando) in enumerate(botones):
            row = i // 2
            col = i % 2
            
            btn = tk.Button(
                botones_frame,
                text=texto,
                font=("Arial", 14, "bold"),
                bg="#667eea",
                fg="white",
                width=25,
                height=3,
                cursor="hand2",
                command=comando
            )
            btn.grid(row=row, column=col, padx=15, pady=15)
    
    def consultar_saldo(self):
        """Consulta el saldo actual"""
        self.actualizar_saldo()
        messagebox.showinfo(
            "Saldo Disponible",
            f"Su saldo actual es:\n\n${self.usuario_actual['saldo']:,.2f} COP"
        )
    
    def retirar_dinero(self):
        """Interfaz para retirar dinero"""
        self.limpiar_ventana()
        
        main_frame = tk.Frame(self.root, bg="#1e293b")
        main_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        tk.Label(
            main_frame,
            text="💰 RETIRAR DINERO",
            font=("Arial", 24, "bold"),
            bg="#1e293b",
            fg="#667eea"
        ).pack(pady=20)
        
        # Mostrar saldo actual
        self.actualizar_saldo()
        tk.Label(
            main_frame,
            text=f"Saldo disponible: ${self.usuario_actual['saldo']:,.2f} COP",
            font=("Arial", 14),
            bg="#1e293b",
            fg="#cbd5e1"
        ).pack(pady=10)
        
        # Entry para el monto
        tk.Label(
            main_frame,
            text="Ingrese el monto a retirar:",
            font=("Arial", 14),
            bg="#1e293b",
            fg="white"
        ).pack(pady=20)
        
        entry_monto = tk.Entry(main_frame, font=("Arial", 16), width=20, justify="center")
        entry_monto.pack(pady=10)
        entry_monto.focus()
        
        # Botones de montos rápidos
        quick_frame = tk.Frame(main_frame, bg="#1e293b")
        quick_frame.pack(pady=20)
        
        montos = [20000, 50000, 100000, 200000, 500000]
        for i, monto in enumerate(montos):
            row = i // 3
            col = i % 3
            btn = tk.Button(
                quick_frame,
                text=f"${monto:,}",
                font=("Arial", 12),
                bg="#334155",
                fg="white",
                width=12,
                command=lambda m=monto: entry_monto.delete(0, tk.END) or entry_monto.insert(0, str(m))
            )
            btn.grid(row=row, column=col, padx=5, pady=5)
        
        def procesar_retiro():
            try:
                monto = float(entry_monto.get())
                if monto <= 0:
                    messagebox.showerror("Error", "El monto debe ser mayor a 0")
                    return
                
                if monto > self.usuario_actual['saldo']:
                    messagebox.showerror("Error", "Saldo insuficiente")
                    return
                
                saldo_anterior = self.usuario_actual['saldo']
                nuevo_saldo = saldo_anterior - monto
                
                # Actualizar en la base de datos
                self.cursor.execute(
                    "UPDATE usuarios SET saldo = ? WHERE numero_cuenta = ?",
                    (nuevo_saldo, self.usuario_actual['numero_cuenta'])
                )
                
                # Registrar transacción
                self.cursor.execute('''
                    INSERT INTO transacciones (numero_cuenta, tipo, monto, saldo_anterior, saldo_nuevo, fecha)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (self.usuario_actual['numero_cuenta'], "RETIRO", monto, saldo_anterior, nuevo_saldo, 
                      datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                self.conn.commit()
                self.usuario_actual['saldo'] = nuevo_saldo
                
                messagebox.showinfo(
                    "Retiro Exitoso",
                    f"Retiro realizado con éxito\n\nMonto retirado: ${monto:,.2f}\nNuevo saldo: ${nuevo_saldo:,.2f}"
                )
                self.mostrar_menu_principal()
                
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese un monto válido")
        
        # Botones de acción
        btn_frame = tk.Frame(main_frame, bg="#1e293b")
        btn_frame.pack(pady=30)
        
        tk.Button(
            btn_frame,
            text="RETIRAR",
            font=("Arial", 14, "bold"),
            bg="#667eea",
            fg="white",
            width=15,
            height=2,
            command=procesar_retiro
        ).pack(side="left", padx=10)
        
        tk.Button(
            btn_frame,
            text="CANCELAR",
            font=("Arial", 14, "bold"),
            bg="#ef4444",
            fg="white",
            width=15,
            height=2,
            command=self.mostrar_menu_principal
        ).pack(side="left", padx=10)
    
    def depositar_dinero(self):
        """Interfaz para depositar dinero"""
        self.limpiar_ventana()
        
        main_frame = tk.Frame(self.root, bg="#1e293b")
        main_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        tk.Label(
            main_frame,
            text="📥 DEPOSITAR DINERO",
            font=("Arial", 24, "bold"),
            bg="#1e293b",
            fg="#667eea"
        ).pack(pady=20)
        
        self.actualizar_saldo()
        tk.Label(
            main_frame,
            text=f"Saldo actual: ${self.usuario_actual['saldo']:,.2f} COP",
            font=("Arial", 14),
            bg="#1e293b",
            fg="#cbd5e1"
        ).pack(pady=10)
        
        tk.Label(
            main_frame,
            text="Ingrese el monto a depositar:",
            font=("Arial", 14),
            bg="#1e293b",
            fg="white"
        ).pack(pady=20)
        
        entry_monto = tk.Entry(main_frame, font=("Arial", 16), width=20, justify="center")
        entry_monto.pack(pady=10)
        entry_monto.focus()
        
        def procesar_deposito():
            try:
                monto = float(entry_monto.get())
                if monto <= 0:
                    messagebox.showerror("Error", "El monto debe ser mayor a 0")
                    return
                
                saldo_anterior = self.usuario_actual['saldo']
                nuevo_saldo = saldo_anterior + monto
                
                self.cursor.execute(
                    "UPDATE usuarios SET saldo = ? WHERE numero_cuenta = ?",
                    (nuevo_saldo, self.usuario_actual['numero_cuenta'])
                )
                
                self.cursor.execute('''
                    INSERT INTO transacciones (numero_cuenta, tipo, monto, saldo_anterior, saldo_nuevo, fecha)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (self.usuario_actual['numero_cuenta'], "DEPOSITO", monto, saldo_anterior, nuevo_saldo,
                      datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                self.conn.commit()
                self.usuario_actual['saldo'] = nuevo_saldo
                
                messagebox.showinfo(
                    "Depósito Exitoso",
                    f"Depósito realizado con éxito\n\nMonto depositado: ${monto:,.2f}\nNuevo saldo: ${nuevo_saldo:,.2f}"
                )
                self.mostrar_menu_principal()
                
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese un monto válido")
        
        btn_frame = tk.Frame(main_frame, bg="#1e293b")
        btn_frame.pack(pady=30)
        
        tk.Button(
            btn_frame,
            text="DEPOSITAR",
            font=("Arial", 14, "bold"),
            bg="#10b981",
            fg="white",
            width=15,
            height=2,
            command=procesar_deposito
        ).pack(side="left", padx=10)
        
        tk.Button(
            btn_frame,
            text="CANCELAR",
            font=("Arial", 14, "bold"),
            bg="#ef4444",
            fg="white",
            width=15,
            height=2,
            command=self.mostrar_menu_principal
        ).pack(side="left", padx=10)
    
    def transferir(self):
        """Interfaz para transferir dinero"""
        self.limpiar_ventana()
        
        main_frame = tk.Frame(self.root, bg="#1e293b")
        main_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        tk.Label(
            main_frame,
            text="💸 TRANSFERIR DINERO",
            font=("Arial", 24, "bold"),
            bg="#1e293b",
            fg="#667eea"
        ).pack(pady=20)
        
        self.actualizar_saldo()
        tk.Label(
            main_frame,
            text=f"Saldo disponible: ${self.usuario_actual['saldo']:,.2f} COP",
            font=("Arial", 14),
            bg="#1e293b",
            fg="#cbd5e1"
        ).pack(pady=10)
        
        form_frame = tk.Frame(main_frame, bg="#334155")
        form_frame.pack(pady=20, padx=50, fill="x")
        
        tk.Label(
            form_frame,
            text="Cuenta destino:",
            font=("Arial", 12),
            bg="#334155",
            fg="white"
        ).pack(pady=(20, 5))
        
        entry_cuenta = tk.Entry(form_frame, font=("Arial", 14), width=25, justify="center")
        entry_cuenta.pack(pady=5)
        
        tk.Label(
            form_frame,
            text="Monto a transferir:",
            font=("Arial", 12),
            bg="#334155",
            fg="white"
        ).pack(pady=(15, 5))
        
        entry_monto = tk.Entry(form_frame, font=("Arial", 14), width=25, justify="center")
        entry_monto.pack(pady=(5, 20))
        
        def procesar_transferencia():
            cuenta_destino = entry_cuenta.get()
            try:
                monto = float(entry_monto.get())
                
                if not cuenta_destino:
                    messagebox.showerror("Error", "Ingrese una cuenta destino")
                    return
                
                if cuenta_destino == self.usuario_actual['numero_cuenta']:
                    messagebox.showerror("Error", "No puede transferir a su propia cuenta")
                    return
                
                if monto <= 0:
                    messagebox.showerror("Error", "El monto debe ser mayor a 0")
                    return
                
                if monto > self.usuario_actual['saldo']:
                    messagebox.showerror("Error", "Saldo insuficiente")
                    return
                
                # Verificar que existe la cuenta destino
                self.cursor.execute("SELECT * FROM usuarios WHERE numero_cuenta = ?", (cuenta_destino,))
                destinatario = self.cursor.fetchone()
                
                if not destinatario:
                    messagebox.showerror("Error", "La cuenta destino no existe")
                    return
                
                # Realizar transferencia
                saldo_anterior = self.usuario_actual['saldo']
                nuevo_saldo = saldo_anterior - monto
                
                # Actualizar cuenta origen
                self.cursor.execute(
                    "UPDATE usuarios SET saldo = ? WHERE numero_cuenta = ?",
                    (nuevo_saldo, self.usuario_actual['numero_cuenta'])
                )
                
                # Actualizar cuenta destino
                nuevo_saldo_destino = destinatario[4] + monto
                self.cursor.execute(
                    "UPDATE usuarios SET saldo = ? WHERE numero_cuenta = ?",
                    (nuevo_saldo_destino, cuenta_destino)
                )
                
                # Registrar transacciones
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.cursor.execute('''
                    INSERT INTO transacciones (numero_cuenta, tipo, monto, saldo_anterior, saldo_nuevo, fecha)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (self.usuario_actual['numero_cuenta'], f"TRANSFERENCIA A {cuenta_destino}", 
                      monto, saldo_anterior, nuevo_saldo, fecha))
                
                self.cursor.execute('''
                    INSERT INTO transacciones (numero_cuenta, tipo, monto, saldo_anterior, saldo_nuevo, fecha)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (cuenta_destino, f"TRANSFERENCIA DE {self.usuario_actual['numero_cuenta']}", 
                      monto, destinatario[4], nuevo_saldo_destino, fecha))
                
                self.conn.commit()
                self.usuario_actual['saldo'] = nuevo_saldo
                
                messagebox.showinfo(
                    "Transferencia Exitosa",
                    f"Transferencia realizada con éxito\n\nDestino: {destinatario[3]}\nMonto: ${monto:,.2f}\nNuevo saldo: ${nuevo_saldo:,.2f}"
                )
                self.mostrar_menu_principal()
                
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese un monto válido")
        
        btn_frame = tk.Frame(main_frame, bg="#1e293b")
        btn_frame.pack(pady=30)
        
        tk.Button(
            btn_frame,
            text="TRANSFERIR",
            font=("Arial", 14, "bold"),
            bg="#667eea",
            fg="white",
            width=15,
            height=2,
            command=procesar_transferencia
        ).pack(side="left", padx=10)
        
        tk.Button(
            btn_frame,
            text="CANCELAR",
            font=("Arial", 14, "bold"),
            bg="#ef4444",
            fg="white",
            width=15,
            height=2,
            command=self.mostrar_menu_principal
        ).pack(side="left", padx=10)
    
    def ver_movimientos(self):
        """Muestra el historial de movimientos"""
        self.limpiar_ventana()
        
        main_frame = tk.Frame(self.root, bg="#1e293b")
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)
        
        tk.Label(
            main_frame,
            text="HISTORIAL DE MOVIMIENTOS",
            font=("Arial", 24, "bold"),
            bg="#1e293b",
            fg="#667eea"
        ).pack(pady=20)
        
        # Frame para la tabla
        table_frame = tk.Frame(main_frame, bg="#1e293b")
        table_frame.pack(fill="both", expand=True, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview
        columns = ("Fecha", "Tipo", "Monto", "Saldo Nuevo")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set, height=12)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=180, anchor="center")
        
        scrollbar.config(command=tree.yview)
        tree.pack(fill="both", expand=True)
        
        # Obtener transacciones
        self.cursor.execute('''
            SELECT fecha, tipo, monto, saldo_nuevo
            FROM transacciones
            WHERE numero_cuenta = ?
            ORDER BY fecha DESC
            LIMIT 50
        ''', (self.usuario_actual['numero_cuenta'],))
        
        transacciones = self.cursor.fetchall()
        
        for trans in transacciones:
            fecha = trans[0].split()[0]  # Solo la fecha
            tipo = trans[1]
            monto = f"${trans[2]:,.2f}"
            saldo = f"${trans[3]:,.2f}"
            tree.insert("", "end", values=(fecha, tipo, monto, saldo))
        
        if not transacciones:
            tk.Label(
                main_frame,
                text="No hay movimientos registrados",
                font=("Arial", 14),
                bg="#1e293b",
                fg="#cbd5e1"
            ).pack(pady=20)
        
        tk.Button(
            main_frame,
            text="VOLVER",
            font=("Arial", 14, "bold"),
            bg="#667eea",
            fg="white",
            width=20,
            height=2,
            command=self.mostrar_menu_principal
        ).pack(pady=20)
    
    def actualizar_saldo(self):
        """Actualiza el saldo del usuario desde la base de datos"""
        self.cursor.execute(
            "SELECT saldo FROM usuarios WHERE numero_cuenta = ?",
            (self.usuario_actual['numero_cuenta'],)
        )
        saldo = self.cursor.fetchone()
        if saldo:
            self.usuario_actual['saldo'] = saldo[0]
    
    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        self.usuario_actual = None
        self.mostrar_login()
    
    def __del__(self):
        """Cierra la conexión a la base de datos"""
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = CajeroAutomatico(root)
    root.mainloop()