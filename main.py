import sys
import os
import shutil
import sqlite3
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from banco_de_arquivos import Ui_telaPrincipal
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog, QMenu, QAction, QDialog, QVBoxLayout, QLabel, QProgressBar


class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processando Arquivos")
        self.setFixedSize(400, 120)
        self.setModal(True)
                # Carregar ícone de arquivo externo
        try:
            icon = QtGui.QIcon("logoSpike.png")  # Ou .ico, .jpg, etc.
            self.setWindowIcon(icon)
        except:
            # Fallback para ícone simples se o arquivo não existir
            pixmap = QtGui.QPixmap(32, 32)
            pixmap.fill(QtGui.QColor("#0078d4"))
            self.setWindowIcon(QtGui.QIcon(pixmap)) 
        layout = QVBoxLayout()
        self.status_label = QLabel("Iniciando processamento...")
        layout.addWidget(self.status_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        self.cancel_button = QtWidgets.QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.cancel_operation)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)
        self.is_cancelled = False
        
    def cancel_operation(self):
        self.is_cancelled = True
        self.status_label.setText("Cancelando operação...")
        self.cancel_button.setEnabled(False)


class DatabaseManager:
    def __init__(self, db_path="file_database.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_name TEXT NOT NULL,
                stored_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                category TEXT,
                tags TEXT,
                description TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP)''')
        conn.commit()
        conn.close()
    
    def add_file(self, original_name, stored_name, file_path, file_size, file_type, category="Outros", tags="", description=""):
        """Adicionar arquivo ao banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO files 
            (original_name, stored_name, file_path, file_size, file_type, category, tags, description, date_added, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (original_name, stored_name, file_path, file_size, file_type, category, tags, description, datetime.now(), datetime.now()))
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return file_id
    
    def get_all_files(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM files ORDER BY date_added DESC''')
        files = cursor.fetchall()
        conn.close()
        return files
    
    def search_files(self, search_term):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM files 
            WHERE original_name LIKE ? OR category LIKE ? OR tags LIKE ? OR description LIKE ?
            ORDER BY date_added DESC
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        files = cursor.fetchall()
        conn.close()
        return files
    
    def update_file_access(self, file_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE files SET last_accessed = ? WHERE id = ?
        ''', (datetime.now(), file_id))
        conn.commit()
        conn.close()
    
    def delete_file(self, file_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
        conn.commit()
        conn.close()


class FileOrganizerThread(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, list)
    
    def __init__(self, source_folder, storage_folder, category="Outros", file_extensions=None):
        super().__init__()
        self.source_folder = source_folder
        self.storage_folder = storage_folder
        self.category = category
        self.file_extensions = file_extensions if file_extensions else ["*"]  # Todos os arquivos
        self.is_running = True
        
    def run(self):
        try:
            self.status_updated.emit("Iniciando organização de arquivos...")
            
            if not os.path.exists(self.source_folder):
                self.status_updated.emit("Erro: Pasta de origem não encontrada!")
                self.finished_signal.emit(False, [])
                return
                
            # Criar pasta de armazenamento se não existir
            os.makedirs(self.storage_folder, exist_ok=True)
            # Procurar arquivos
            files = []
            for root, dirs, filenames in os.walk(self.source_folder):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    # Se file_extensions é ["*"], aceita todos os arquivos
                    if "*" in self.file_extensions:
                        files.append(file_path)
                    else:
                        # Verificar extensão do arquivo
                        file_ext = os.path.splitext(filename)[1].lower()
                        if file_ext in [ext.lower() for ext in self.file_extensions]:
                            files.append(file_path)
            total_files = len(files)
            self.status_updated.emit(f"Encontrados {total_files} arquivos")
            
            if total_files == 0:
                self.status_updated.emit("Nenhum arquivo encontrado!")
                self.finished_signal.emit(True, [])
                return
            
            # Processar arquivos
            processed_files = []
            for i, file_path in enumerate(files):
                if not self.is_running:
                    break
                    
                try:
                    original_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    file_ext = os.path.splitext(original_name)[1].lower()
                    
                    # Determinar tipo de arquivo baseado na extensão
                    file_type = self.get_file_type(file_ext)
                    
                    # Gerar nome único para armazenamento
                    base_name, ext = os.path.splitext(original_name)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    stored_name = f"{base_name}_{timestamp}{ext}"
                    stored_path = os.path.join(self.storage_folder, stored_name)
                    
                    # Copiar arquivo para pasta interna
                    shutil.copy2(file_path, stored_path)
                    
                    processed_files.append({
                        'original_name': original_name,
                        'stored_name': stored_name,
                        'file_path': stored_path,
                        'file_size': file_size,
                        'file_type': file_type,
                        'file_extension': file_ext})
                    progress = int((i + 1) / total_files * 100)
                    self.progress_updated.emit(progress)
                    self.status_updated.emit(f"Processado: {original_name}") 
                except Exception as e:
                    self.status_updated.emit(f"Erro ao processar {original_name}: {str(e)}")
            if self.is_running:
                self.status_updated.emit(f"Concluído! {len(processed_files)} arquivos processados.")
                self.finished_signal.emit(True, processed_files)
            else:
                self.status_updated.emit("Operação cancelada pelo usuário.")
                self.finished_signal.emit(False, [])
        except Exception as e:
            self.status_updated.emit(f"Erro crítico: {str(e)}")
            self.finished_signal.emit(False, [])
    
    def get_file_type(self, file_ext):
        """Determinar o tipo de arquivo baseado na extensão"""
        file_types = {
            '.pdf': 'PDF',
            '.doc': 'Documento Word',
            '.docx': 'Documento Word',
            '.xls': 'Planilha Excel',
            '.xlsx': 'Planilha Excel',
            '.ppt': 'Apresentação PowerPoint',
            '.pptx': 'Apresentação PowerPoint',
            '.txt': 'Texto',
            '.jpg': 'Imagem',
            '.jpeg': 'Imagem',
            '.png': 'Imagem',
            '.gif': 'Imagem',
            '.bmp': 'Imagem',
            '.mp4': 'Vídeo',
            '.avi': 'Vídeo',
            '.mkv': 'Vídeo',
            '.mp3': 'Áudio',
            '.wav': 'Áudio',
            '.zip': 'Arquivo Compactado',
            '.rar': 'Arquivo Compactado',
            '.7z': 'Arquivo Compactado',
            '.dwg': 'Desenho CAD',
            '.dxf': 'Desenho CAD',}
        return file_types.get(file_ext.lower(), 'Arquivo')
    def stop(self):
        self.is_running = False

class FileSearchThread(QThread):
    search_finished = pyqtSignal(list)
    
    def __init__(self, db_manager, search_term=""):
        super().__init__()
        self.db_manager = db_manager
        self.search_term = search_term
        self.is_running = True
        
    def run(self):
        try:
            if self.search_term:
                files = self.db_manager.search_files(self.search_term)
            else:
                files = self.db_manager.get_all_files()
            if self.is_running:
                self.search_finished.emit(files)
        except Exception as e:
            print(f"Erro na busca: {e}")
            self.search_finished.emit([])
    
    def stop(self):
        self.is_running = False

class DownloadThread(QThread):
    download_finished = pyqtSignal(bool, str)
    progress_updated = pyqtSignal(int)

    def __init__(self, source_path, destination_path):
        super().__init__()
        self.source_path = source_path
        self.destination_path = destination_path
        
    def run(self):
        try:
            self.progress_updated.emit(10)
            
            if not os.path.exists(self.source_path):
                self.download_finished.emit(False, "Arquivo não encontrado no banco de dados")
                return
            
            # Criar diretório de destino se não existir
            os.makedirs(os.path.dirname(self.destination_path), exist_ok=True)
            self.progress_updated.emit(50)
            
            # Copiar arquivo
            shutil.copy2(self.source_path, self.destination_path)
            self.progress_updated.emit(100)
            self.download_finished.emit(True, f"Arquivo baixado com sucesso para: {self.destination_path}")
        except Exception as e:
            self.download_finished.emit(False, f"Erro ao baixar arquivo: {str(e)}")


class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_telaPrincipal()
        self.ui.setupUi(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/logoSpike.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        # Configurações iniciais
        self.storage_folder = "arquivos_armazenados"
        
        # Inicializar banco de dados
        self.db_manager = DatabaseManager()
        
        # Threads
        self.organizer_thread = None
        self.search_thread = None
        self.download_thread = None
        
        # Dialog de progresso
        self.progress_dialog = None
        
        # Configurar interface
        self.setup_connections()
        self.setup_tree_widget()
        
        # Aplicar estilo
        self.apply_styles()
        
        # Carregar arquivos do banco de dados
        self.load_files_from_database()
        
    def setup_connections(self):
        self.ui.btn_procurar.clicked.connect(self.search_files)
        self.ui.btn_add.clicked.connect(self.add_files)
        self.ui.btn_atualizar.clicked.connect(self.refresh_files)
        
        # Conectar busca com Enter
        self.ui.search_edit.returnPressed.connect(self.search_files)
        
        # Conectar duplo clique na tree
        self.ui.treeWidget.itemDoubleClicked.connect(self.on_item_double_click)
        
        # Conectar menu de contexto
        self.ui.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.treeWidget.customContextMenuRequested.connect(self.show_context_menu)
        
    def setup_tree_widget(self):
        """Configurar a tree widget"""
        self.ui.treeWidget.setColumnCount(7)  # Adicionada coluna para ações
        self.ui.treeWidget.setHeaderLabels(["ID", "Nome do Arquivo", "Tamanho", "Tipo", "Categoria", "Data de Adição", "Ações"])
        
        # Ajustar largura das colunas
        self.ui.treeWidget.setColumnWidth(0, 50)   # ID
        self.ui.treeWidget.setColumnWidth(1, 250)  # Nome
        self.ui.treeWidget.setColumnWidth(2, 100)  # Tamanho
        self.ui.treeWidget.setColumnWidth(3, 120)  # Tipo
        self.ui.treeWidget.setColumnWidth(4, 150)  # Categoria
        self.ui.treeWidget.setColumnWidth(5, 120)  # Data
        self.ui.treeWidget.setColumnWidth(6, 100)  # Ações
        # Permitir ordenação
        self.ui.treeWidget.setSortingEnabled(True)
        
    def apply_styles(self):
        self.ui.treeWidget.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            QTreeWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;}""")
        
        self.ui.search_edit.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;}""")
        
        self.ui.btn_procurar.setStyleSheet("""
            QPushButton {
                background-color: rgb(182, 0, 0);
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgb(255, 0, 0);
                color: rgb(0, 0, 0) 
            }
            QPushButton:pressed {
                background-color: rgb(255, 255, 255);
                color: rgb(0, 0, 0)} """)
        self.ui.btn_add.setStyleSheet("""
            QPushButton {
                background-color: rgb(182, 0, 0);
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgb(255, 0, 0);
                color: rgb(0, 0, 0)   
            }
            QPushButton:pressed {
                background-color: rgb(255, 255, 255);
                color: rgb(0, 0, 0)}""")
        self.ui.btn_atualizar.setStyleSheet("""
            QPushButton {
                background-color: rgb(182, 0, 0);
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgb(255, 0, 0);
                color: rgb(0, 0, 0) 
            }
            QPushButton:pressed {
                background-color: rgb(255, 255, 255);
                color: rgb(0, 0, 0)} """)
        
    def format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names)-1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def format_date(self, date_string):
        try:
            if isinstance(date_string, str):
                dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            else:
                dt = date_string
            return dt.strftime("%d/%m/%Y %H:%M")
        except:
            return date_string
        
    def load_files_from_database(self, search_term=""):
        self.search_thread = FileSearchThread(self.db_manager, search_term)
        self.search_thread.search_finished.connect(self.display_files)
        self.search_thread.start()
        
    def display_files(self, files):
        self.ui.treeWidget.clear()
        
        if not files:
            item = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
            item.setText(1, "Nenhum arquivo encontrado")
            return
        
        for file_data in files:
            item = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
            item.setText(0, str(file_data[0]))  # ID
            item.setText(1, file_data[1])       # Nome original
            item.setText(2, self.format_file_size(file_data[4]))  # Tamanho
            item.setText(3, file_data[5])       # Tipo
            item.setText(4, file_data[6])       # Categoria
            item.setText(5, self.format_date(file_data[9]))  # Data de adição
            item.setText(6, "📥 Download")      # Botão de download
            # Armazenar dados completos no item
            item.setData(0, QtCore.Qt.UserRole, file_data)
            
    def show_context_menu(self, position):
        item = self.ui.treeWidget.itemAt(position)
        if item:
            file_data = item.data(0, QtCore.Qt.UserRole)
            if file_data:
                menu = QMenu(self)
                
                # Ação de download
                download_action = QAction("📥 Download Arquivo", self)
                download_action.triggered.connect(lambda: self.download_file(file_data))
                menu.addAction(download_action)
                
                # Ação de abrir
                open_action = QAction("🔓 Abrir Arquivo", self)
                open_action.triggered.connect(lambda: self.open_file(file_data))
                menu.addAction(open_action)
                
                # Separador
                menu.addSeparator()

                # Ação de informações
                info_action = QAction("ℹ️ Informações", self)
                info_action.triggered.connect(lambda: self.show_file_info(file_data))
                menu.addAction(info_action)
                menu.exec_(self.ui.treeWidget.viewport().mapToGlobal(position))
    
    def download_file(self, file_data):
        original_name = file_data[1]  # Nome original
        stored_path = file_data[3]    # Caminho armazenado
        # Perguntar onde salvar
        destination_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Salvar Arquivo", 
            original_name,
            f"Todos os arquivos (*.*)")
        if destination_path:
            # Criar dialog de progresso para download
            download_dialog = ProgressDialog(self)
            download_dialog.setWindowTitle("Download em Andamento")
            download_dialog.status_label.setText("Iniciando download...") 
            # Iniciar thread de download
            self.download_thread = DownloadThread(stored_path, destination_path)
            self.download_thread.download_finished.connect(
                lambda success, msg: self.download_finished(success, msg, download_dialog))
            self.download_thread.progress_updated.connect(download_dialog.progress_bar.setValue)
            self.download_thread.start()
            # Mostrar dialog de progresso
            download_dialog.exec_()
    
    def download_finished(self, success, message, dialog):
        dialog.close()
        if success:
            QMessageBox.information(self, "Sucesso", message)
        else:
            QMessageBox.warning(self, "Erro", message)
    
    def open_file(self, file_data):
        file_path = file_data[3]  # Caminho armazenado
        if os.path.exists(file_path):
            # Atualizar último acesso
            self.db_manager.update_file_access(file_data[0])
            # Abrir arquivo
            try:
                if sys.platform == "win32":
                    os.startfile(file_path)
                else:
                    QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(file_path))
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível abrir o arquivo: {str(e)}")
        else:
            QMessageBox.warning(self, "Erro", "Arquivo não encontrado!")
    
    def show_file_info(self, file_data):
        info_text = f"""
        <b>Informações do Arquivo:</b><br><br>
        <b>ID:</b> {file_data[0]}<br>
        <b>Nome Original:</b> {file_data[1]}<br>
        <b>Nome Armazenado:</b> {file_data[2]}<br>
        <b>Tamanho:</b> {self.format_file_size(file_data[4])}<br>
        <b>Tipo:</b> {file_data[5]}<br>
        <b>Categoria:</b> {file_data[6]}<br>
        <b>Tags:</b> {file_data[7] or 'Nenhuma'}<br>
        <b>Descrição:</b> {file_data[8] or 'Nenhuma'}<br>
        <b>Data de Adição:</b> {self.format_date(file_data[9])}<br>
        <b>Último Acesso:</b> {self.format_date(file_data[10]) if file_data[10] else 'Nunca'}<br>
        <b>Caminho:</b> {file_data[3]}"""
        QMessageBox.information(self, "Informações do Arquivo", info_text)
            
    def search_files(self):
        search_text = self.ui.search_edit.text().strip()
        self.load_files_from_database(search_text)
        
    def add_files(self):
        # Opções para o usuário escolher
        options = QMessageBox()
        options.setWindowTitle("Selecionar Tipo de Arquivo")
        options.setText("Como deseja adicionar arquivos?")
        options.setIcon(QMessageBox.Question)
        # Botões
        all_files_btn = options.addButton("Todos os Arquivos", QMessageBox.ActionRole)
        specific_type_btn = options.addButton("Tipo Específico", QMessageBox.ActionRole)
        cancel_btn = options.addButton("Cancelar", QMessageBox.RejectRole)
        options.exec_()
        clicked_button = options.clickedButton()
        if clicked_button == cancel_btn:
            return
        elif clicked_button == all_files_btn:
            # Adicionar todos os tipos de arquivo
            file_extensions = ["*"]
            file_type_desc = "todos os tipos de arquivo"
        else:
            # Selecionar tipo específico
            file_types = [
                "Todos os Arquivos (*.*)",
                "Documentos PDF (*.pdf)",
                "Documentos Word (*.doc *.docx)",
                "Planilhas Excel (*.xls *.xlsx)",
                "Imagens (*.jpg *.jpeg *.png *.gif *.bmp)",
                "Vídeos (*.mp4 *.avi *.mkv)",
                "Áudios (*.mp3 *.wav)",
                "Arquivos CAD (*.dwg *.dxf)",
                "Arquivos Compactados (*.zip *.rar *.7z)"]
            file_type, ok = QInputDialog.getItem(
                self, "Selecionar Tipo de Arquivo", 
                "Escolha o tipo de arquivo:", file_types, 0, False)
            if not ok:
                return
            
            # Mapear seleção para extensões
            extension_map = {
                "Todos os Arquivos (*.*)": ["*"], "Documentos PDF (*.pdf)": [".pdf"],
                "Documentos Word (*.doc *.docx)": [".doc", ".docx"],
                "Planilhas Excel (*.xls *.xlsx)": [".xls", ".xlsx"],
                "Imagens (*.jpg *.jpeg *.png *.gif *.bmp)": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
                "Vídeos (*.mp4 *.avi *.mkv)": [".mp4", ".avi", ".mkv"],
                "Áudios (*.mp3 *.wav)": [".mp3", ".wav"],
                "Arquivos CAD (*.dwg *.dxf)": [".dwg", ".dxf"],
                "Arquivos Compactados (*.zip *.rar *.7z)": [".zip", ".rar", ".7z"]}
            file_extensions = extension_map.get(file_type, ["*"])
            file_type_desc = file_type.split("(")[0].strip()
        # Perguntar pasta de origem
        source_folder = QFileDialog.getExistingDirectory(self, "Selecionar pasta com arquivos")
        if not source_folder:
            return
        
        # Perguntar categoria
        category, ok = QInputDialog.getText(self, "Categoria", "Digite a categoria do arquivo:")
        if not ok:
            category = "Outros"
        
        # Iniciar organização
        self.start_organization(source_folder, category, file_extensions, file_type_desc)
        
    def start_organization(self, source_folder, category, file_extensions, file_type_desc):
        # Criar e mostrar dialog de progresso
        self.progress_dialog = ProgressDialog(self)
        self.progress_dialog.cancel_button.clicked.connect(self.cancel_organization)
        # Desabilitar botões durante a operação
        self.ui.btn_add.setEnabled(False)
        self.ui.btn_procurar.setEnabled(False)
        self.ui.btn_atualizar.setEnabled(False)
        # Iniciar thread de organização
        self.organizer_thread = FileOrganizerThread(
            source_folder, 
            self.storage_folder, 
            category,
            file_extensions)
        self.organizer_thread.progress_updated.connect(self.progress_dialog.progress_bar.setValue)
        self.organizer_thread.status_updated.connect(self.progress_dialog.status_label.setText)
        self.organizer_thread.finished_signal.connect(self.organization_finished)
        self.organizer_thread.start()
        # Mostrar dialog de progresso
        self.progress_dialog.exec_()
        
    def cancel_organization(self):
        if self.organizer_thread and self.organizer_thread.isRunning():
            self.organizer_thread.stop()
            self.progress_dialog.status_label.setText("Cancelando...")
            self.progress_dialog.cancel_button.setEnabled(False)
        
    def organization_finished(self, success, processed_files):
        # Fechar dialog de progresso
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        if success and processed_files:
            # Salvar no banco de dados
            for file_info in processed_files:
                self.db_manager.add_file(
                    original_name=file_info['original_name'],
                    stored_name=file_info['stored_name'],
                    file_path=file_info['file_path'],
                    file_size=file_info['file_size'],
                    file_type=file_info['file_type'],
                    category=self.organizer_thread.category)
            QMessageBox.information(self, "Sucesso", f"{len(processed_files)} arquivos adicionados ao banco de dados!")
            # Atualizar lista
            self.load_files_from_database()
        # Reabilitar botões
        self.ui.btn_add.setEnabled(True)
        self.ui.btn_procurar.setEnabled(True)
        self.ui.btn_atualizar.setEnabled(True)
            
    def refresh_files(self):
        self.load_files_from_database(self.ui.search_edit.text().strip())
        
    def on_item_double_click(self, item, column):
        file_data = item.data(0, QtCore.Qt.UserRole)
        if file_data:
            if column == 6:  # Coluna "Ações"
                self.download_file(file_data)
            else:
                self.open_file(file_data)
                
    def closeEvent(self, event):
        if self.organizer_thread and self.organizer_thread.isRunning():
            self.organizer_thread.stop()
            self.organizer_thread.wait()
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.stop()
            self.search_thread.wait()
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()
            self.download_thread.wait()  
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # Criar e mostrar a janela principal
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())