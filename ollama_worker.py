#!/usr/bin/env python3
"""
Ollama Worker - VERSIONE CORRETTA con gestione timeout migliorata
"""

import json
import requests
import threading
import time
import random
from enum import Enum
from typing import List, Dict, Optional, Any, Iterator
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition


class OllamaError(Exception):
    """Eccezione personalizzata per errori Ollama"""
    pass


class RequestState(Enum):
    """Stati delle richieste"""
    IDLE = "idle"
    CONNECTING = "connecting" 
    STREAMING = "streaming"
    COMPLETED = "completed"
    STOPPED = "stopped"
    ERROR = "error"


class RequestManager:
    """Pure networking layer with FIXED timeout handling"""
    
    def __init__(self, base_url: str, connection_timeout: int = 10, read_timeout: int = 60, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.connection_timeout = connection_timeout
        self.read_timeout = read_timeout  # NUOVO: timeout separato per la lettura
        self.max_retries = max_retries
        self.session = requests.Session()
        self.state = RequestState.IDLE
        
        # Headers di default
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'OllamaChat/1.0'
        })
        
        print(f"DEBUG: RequestManager initialized with connection_timeout={connection_timeout}, read_timeout={read_timeout}")
    
    def _exponential_backoff(self, attempt: int) -> float:
        """Calcola delay per retry con backoff esponenziale"""
        base_delay = 1.0
        max_delay = 30.0
        delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
        return delay
    
    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determina se ritentare la richiesta"""
        if attempt >= self.max_retries:
            return False
        
        # Retry per errori di rete temporanei
        if isinstance(exception, (requests.exceptions.ConnectionError,
                                requests.exceptions.Timeout)):
            return True
        
        # Retry per status code 5xx
        if isinstance(exception, requests.exceptions.HTTPError):
            if exception.response and 500 <= exception.response.status_code < 600:
                return True
        
        return False
    
    def get_models(self) -> List[str]:
        """Recupera la lista dei modelli disponibili con retry"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                print(f"DEBUG: Getting models (attempt {attempt + 1})")
                self.state = RequestState.CONNECTING
                
                # USA SOLO CONNECTION TIMEOUT per le richieste non-streaming
                response = self.session.get(
                    f"{self.base_url}/api/tags",
                    timeout=self.connection_timeout
                )
                response.raise_for_status()
                
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                self.state = RequestState.COMPLETED
                print(f"DEBUG: Found {len(models)} models")
                return sorted(models)
                
            except Exception as e:
                last_exception = e
                self.state = RequestState.ERROR
                print(f"DEBUG: Error getting models (attempt {attempt + 1}): {e}")
                
                if self._should_retry(e, attempt):
                    delay = self._exponential_backoff(attempt)
                    print(f"DEBUG: Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    break
        
        # Se arriviamo qui, tutti i retry sono falliti
        raise OllamaError(f"Errore nel recuperare i modelli: {str(last_exception)}")
    
    def chat_stream(self, model: str, messages: List[Dict], 
                   options: Dict = None, stop_event: threading.Event = None) -> Iterator[Dict]:
        """Invia una richiesta di chat con streaming e TIMEOUT CORRETTO"""
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        if options:
            payload["options"] = options
        
        print(f"DEBUG: Starting chat stream with model={model}")
        print(f"DEBUG: Using timeout=(connect={self.connection_timeout}, read={self.read_timeout})")
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                self.state = RequestState.CONNECTING
                print(f"DEBUG: Chat stream attempt {attempt + 1}")
                
                # Controllo stop prima di iniziare
                if stop_event and stop_event.is_set():
                    print("DEBUG: Stop requested before connection")
                    self.state = RequestState.STOPPED
                    return
                
                # USA TIMEOUT SEPARATI: connection per connessione, read per stream
                response = self.session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    stream=True,
                    timeout=(self.connection_timeout, self.read_timeout)  # CORRETTO!
                )
                response.raise_for_status()
                
                self.state = RequestState.STREAMING
                print("DEBUG: Stream started successfully")
                
                chunk_count = 0
                # Genera i chunk della risposta
                for line in response.iter_lines(chunk_size=1, decode_unicode=True):
                    # Controlla stop ad ogni chunk
                    if stop_event and stop_event.is_set():
                        print("DEBUG: Stop requested during streaming")
                        self.state = RequestState.STOPPED
                        return
                    
                    if line:
                        try:
                            chunk = json.loads(line)
                            chunk_count += 1
                            if chunk_count % 10 == 0:
                                print(f"DEBUG: Processed {chunk_count} chunks")
                            yield chunk
                        except json.JSONDecodeError as je:
                            print(f"DEBUG: JSON decode error: {je}")
                            continue
                
                print(f"DEBUG: Stream completed successfully ({chunk_count} chunks)")
                self.state = RequestState.COMPLETED
                return
                
            except requests.exceptions.Timeout as te:
                last_exception = te
                self.state = RequestState.ERROR
                print(f"DEBUG: Timeout error (attempt {attempt + 1}): {te}")
                
                # Se stop è stato richiesto, non ritentare
                if stop_event and stop_event.is_set():
                    print("DEBUG: Stop requested, not retrying timeout")
                    self.state = RequestState.STOPPED
                    return
                
                if self._should_retry(te, attempt):
                    delay = self._exponential_backoff(attempt)
                    print(f"DEBUG: Retrying timeout in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    print("DEBUG: Max retries reached for timeout")
                    break
                    
            except Exception as e:
                last_exception = e
                self.state = RequestState.ERROR
                print(f"DEBUG: General error (attempt {attempt + 1}): {e}")
                
                # Se stop è stato richiesto, non ritentare
                if stop_event and stop_event.is_set():
                    print("DEBUG: Stop requested, not retrying")
                    self.state = RequestState.STOPPED
                    return
                
                if self._should_retry(e, attempt):
                    delay = self._exponential_backoff(attempt)
                    print(f"DEBUG: Retrying error in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    print("DEBUG: Max retries reached for error")
                    break
        
        # Se arriviamo qui, tutti i retry sono falliti
        if stop_event and stop_event.is_set():
            print("DEBUG: Final state: stopped")
            self.state = RequestState.STOPPED
            return
        
        error_msg = f"Errore nella richiesta di chat: {str(last_exception)}"
        print(f"DEBUG: Final error: {error_msg}")
        raise OllamaError(error_msg)
    
    def test_connection(self) -> bool:
        """Testa la connessione al server Ollama"""
        try:
            print("DEBUG: Testing connection...")
            response = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=self.connection_timeout
            )
            success = response.status_code == 200
            print(f"DEBUG: Connection test result: {success}")
            return success
        except Exception as e:
            print(f"DEBUG: Connection test failed: {e}")
            return False


class ConversationManager:
    """Thread-safe conversation cache with intelligent trimming"""
    
    def __init__(self, max_messages: int = 100):
        self.messages: List[Dict[str, str]] = []
        self.max_messages = max_messages
        self.mutex = QMutex()
    
    def add_message(self, role: str, content: str):
        """Aggiunge un messaggio alla conversazione thread-safe"""
        self.mutex.lock()
        try:
            self.messages.append({
                "role": role,
                "content": content,
                "timestamp": time.time()
            })
            
            self._trim_messages()
            
        finally:
            self.mutex.unlock()
    
    def _trim_messages(self):
        """Mantieni solo gli ultimi N messaggi preservando il system message"""
        if len(self.messages) <= self.max_messages:
            return
        
        # Separa system messages dagli altri
        system_messages = [msg for msg in self.messages if msg['role'] == 'system']
        other_messages = [msg for msg in self.messages if msg['role'] != 'system']
        
        if system_messages:
            # Mantieni system messages + ultimi messaggi fino al limite
            keep_count = self.max_messages - len(system_messages)
            self.messages = system_messages + other_messages[-keep_count:]
        else:
            # Solo ultimi messaggi
            self.messages = self.messages[-self.max_messages:]
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Restituisce i messaggi per l'API Ollama (thread-safe)"""
        self.mutex.lock()
        try:
            # Rimuovi timestamp per l'API
            return [{"role": msg["role"], "content": msg["content"]} 
                   for msg in self.messages]
        finally:
            self.mutex.unlock()
    
    def clear(self):
        """Pulisce la conversazione"""
        self.mutex.lock()
        try:
            self.messages.clear()
        finally:
            self.mutex.unlock()
    
    def get_message_count(self) -> int:
        """Restituisce il numero di messaggi"""
        self.mutex.lock()
        try:
            return len(self.messages)
        finally:
            self.mutex.unlock()
    
    def set_system_message(self, content: str):
        """Imposta o aggiorna il messaggio di sistema"""
        self.mutex.lock()
        try:
            # Rimuovi eventuali messaggi di sistema esistenti
            self.messages = [msg for msg in self.messages if msg['role'] != 'system']
            
            # Aggiungi il nuovo messaggio di sistema all'inizio
            if content.strip():
                self.messages.insert(0, {
                    "role": "system",
                    "content": content,
                    "timestamp": time.time()
                })
        finally:
            self.mutex.unlock()


class OllamaWorker(QThread):
    """Orchestrator con TIMEOUT MANAGEMENT MIGLIORATO"""
    
    # Segnali - INTERFACCIA PUBBLICA INVARIATA
    models_received = pyqtSignal(list)
    message_chunk_received = pyqtSignal(str)
    message_completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    connection_status_changed = pyqtSignal(bool)
    generation_stopped = pyqtSignal()
    progress_updated = pyqtSignal(int)
    
    def __init__(self, settings: Dict[str, Any], parent=None):
        super().__init__(parent)
        
        self.settings = settings
        self.request_manager = None
        self.conversation = ConversationManager(settings.get("max_messages", 100))
        
        # Controllo thread
        self.current_task = None
        self.current_model = None
        self.stop_event = threading.Event()
        self.is_busy = False
        
        # Mutex per thread safety
        self.task_mutex = QMutex()
        self.task_condition = QWaitCondition()
        
        self.update_settings(settings)
    
    def update_settings(self, settings: Dict[str, Any]):
        """Aggiorna le impostazioni del worker - CON TIMEOUT MIGLIORATI"""
        self.settings = settings
        
        base_url = settings.get("server_url", "http://localhost:11434")
        connection_timeout = settings.get("connection_timeout", 10)
        # NUOVO: timeout separato per lettura (più lungo per streaming)
        read_timeout = settings.get("read_timeout", 120)  # 2 minuti per lo streaming
        max_retries = settings.get("max_retries", 3)
        
        print(f"DEBUG: Updating RequestManager settings:")
        print(f"  base_url: {base_url}")
        print(f"  connection_timeout: {connection_timeout}")
        print(f"  read_timeout: {read_timeout}")
        print(f"  max_retries: {max_retries}")
        
        self.request_manager = RequestManager(base_url, connection_timeout, read_timeout, max_retries)
        self.conversation.max_messages = settings.get("max_messages", 100)
    
    def set_model(self, model: str):
        """Imposta il modello corrente"""
        self.current_model = model
        print(f"DEBUG: Model set to: {model}")
    
    def load_models(self):
        """Carica i modelli disponibili"""
        self.task_mutex.lock()
        try:
            if self.is_busy:
                print("DEBUG: Worker busy, cannot load models")
                return False
            
            print("DEBUG: Queuing load_models task")
            self.current_task = "load_models"
            self.task_condition.wakeAll()
            
            if not self.isRunning():
                print("DEBUG: Starting worker thread")
                self.start()
            
            return True
        finally:
            self.task_mutex.unlock()
    
    def send_message(self, message: str, context: str = ""):
        """Invia un messaggio"""
        if not self.current_model:
            print("DEBUG: No model selected")
            self.error_occurred.emit("Nessun modello selezionato")
            return False
        
        self.task_mutex.lock()
        try:
            if self.is_busy:
                print("DEBUG: Worker busy, cannot send message")
                return False
            
            # Costruisci il messaggio finale
            final_message = message
            if context.strip():
                print(f"DEBUG: Adding context ({len(context)} chars)")
                final_message = f"{context.strip()}\n\nDOMANDA UTENTE: {message}\n\nRispondi utilizzando le informazioni del contesto quando rilevanti."
            else:
                print("DEBUG: No context provided")
                
            self.conversation.add_message("user", final_message)
            
            print("DEBUG: Queuing send_message task")
            self.current_task = "send_message"
            self.task_condition.wakeAll()
            
            if not self.isRunning():
                print("DEBUG: Starting worker thread")
                self.start()
            
            return True
        finally:
            self.task_mutex.unlock()
    
    def stop_generation(self):
        """Ferma la generazione corrente"""
        print("DEBUG: Stop generation requested")
        self.stop_event.set()
    
    def clear_conversation(self):
        """Pulisce la conversazione"""
        print("DEBUG: Clearing conversation")
        self.conversation.clear()
    
    def set_system_message(self, message: str):
        """Imposta il messaggio di sistema"""
        print(f"DEBUG: Setting system message ({len(message)} chars)")
        self.conversation.set_system_message(message)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Restituisce la cronologia della conversazione"""
        return self.conversation.get_messages()
    
    def is_connected(self) -> bool:
        """Verifica se il server è raggiungibile"""
        if not self.request_manager:
            return False
        return self.request_manager.test_connection()
    
    def run(self):
        """Loop principale del thread con ERROR HANDLING MIGLIORATO"""
        print("DEBUG: Worker thread started")
        
        while not self.isInterruptionRequested():
            self.task_mutex.lock()
            
            # Aspetta un nuovo task
            if not self.current_task:
                self.task_condition.wait(self.task_mutex, 1000)  # Timeout 1 secondo
                
            current_task = self.current_task
            self.current_task = None
            self.task_mutex.unlock()
            
            if not current_task:
                continue
            
            print(f"DEBUG: Processing task: {current_task}")
            self.is_busy = True
            self.stop_event.clear()
            
            try:
                if current_task == "load_models":
                    self._handle_load_models()
                elif current_task == "send_message":
                    self._handle_send_message()
                    
            except Exception as e:
                print(f"DEBUG: Exception in worker: {e}")
                self.error_occurred.emit(f"Errore nel worker: {str(e)}")
            finally:
                self.is_busy = False
                print(f"DEBUG: Task {current_task} completed")
        
        print("DEBUG: Worker thread ended")
    
    def _handle_load_models(self):
        """Gestisce il caricamento dei modelli con ERROR HANDLING"""
        try:
            print("DEBUG: Handling load_models")
            
            # Test connessione
            if not self.request_manager.test_connection():
                print("DEBUG: Connection test failed")
                self.connection_status_changed.emit(False)
                self.error_occurred.emit("Impossibile connettersi al server Ollama. Verifica che sia in esecuzione su localhost:11434")
                return
            
            print("DEBUG: Connection test passed")
            self.connection_status_changed.emit(True)
            
            # Carica modelli
            models = self.request_manager.get_models()
            print(f"DEBUG: Loaded {len(models)} models")
            self.models_received.emit(models)
            
        except OllamaError as e:
            print(f"DEBUG: OllamaError in load_models: {e}")
            self.connection_status_changed.emit(False)
            self.error_occurred.emit(str(e))
        except Exception as e:
            print(f"DEBUG: Unexpected error in load_models: {e}")
            self.connection_status_changed.emit(False)
            self.error_occurred.emit(f"Errore imprevisto: {str(e)}")
    
    def _handle_send_message(self):
        """Gestisce l'invio di un messaggio con TIMEOUT E ERROR HANDLING MIGLIORATI"""
        if not self.current_model:
            print("DEBUG: No model selected for send_message")
            self.error_occurred.emit("Nessun modello selezionato")
            return
        
        # Controlla stop PRIMA di iniziare
        if self.stop_event.is_set():
            print("DEBUG: Stop requested before sending message")
            self.generation_stopped.emit()
            return
        
        try:
            messages = self.conversation.get_messages()
            if not messages:
                print("DEBUG: No messages to send")
                self.error_occurred.emit("Nessun messaggio da inviare")
                return
            
            print(f"DEBUG: Sending {len(messages)} messages to model {self.current_model}")
            
            # Opzioni per il modello
            options = {}
            if "temperature" in self.settings:
                options["temperature"] = self.settings["temperature"]
            if "top_p" in self.settings:
                options["top_p"] = self.settings["top_p"]
            if "top_k" in self.settings:
                options["top_k"] = self.settings["top_k"]
            
            full_response = ""
            chunk_count = 0
            stream_started = False
            
            print("DEBUG: Starting stream...")
            
            try:
                # Stream della risposta con gestione robusta
                stream_iterator = self.request_manager.chat_stream(
                    self.current_model, 
                    messages, 
                    options, 
                    self.stop_event
                )
                
                # Se l'iteratore è None (stop immediato), emetti stopped
                if stream_iterator is None:
                    print("DEBUG: Stream iterator is None (immediate stop)")
                    self.generation_stopped.emit()
                    return
                
                for chunk in stream_iterator:
                    stream_started = True
                    
                    # Doppio controllo stop
                    if self.stop_event.is_set():
                        print("DEBUG: Stop requested during chunk processing")
                        self.generation_stopped.emit()
                        return
                    
                    if 'message' in chunk and 'content' in chunk['message']:
                        content = chunk['message']['content']
                        if content:
                            full_response += content
                            self.message_chunk_received.emit(content)
                            
                            chunk_count += 1
                            
                            # Debug periodico
                            if chunk_count % 50 == 0:
                                print(f"DEBUG: Processed {chunk_count} chunks, response length: {len(full_response)}")
                    
                    # Fine del messaggio
                    if chunk.get('done', False):
                        print("DEBUG: Stream marked as done")
                        break
                
                print(f"DEBUG: Stream completed. Total chunks: {chunk_count}, response length: {len(full_response)}")
                
            except OllamaError as oe:
                print(f"DEBUG: OllamaError during streaming: {oe}")
                if self.stop_event.is_set():
                    self.generation_stopped.emit()
                else:
                    self.error_occurred.emit(str(oe))
                return
                
            except Exception as se:
                print(f"DEBUG: Stream exception: {se}")
                if self.stop_event.is_set():
                    self.generation_stopped.emit()
                else:
                    self.error_occurred.emit(f"Errore durante lo streaming: {str(se)}")
                return
            
            # Gestione completamento o stop
            if self.stop_event.is_set():
                print("DEBUG: Generation was stopped")
                self.generation_stopped.emit()
            elif full_response:
                print(f"DEBUG: Message completed successfully ({len(full_response)} chars)")
                # Aggiungi la risposta alla conversazione
                self.conversation.add_message("assistant", full_response)
                self.message_completed.emit(full_response)
            else:
                print("DEBUG: Empty response received")
                if stream_started:
                    self.message_completed.emit("")
                else:
                    self.error_occurred.emit("Nessuna risposta ricevuta dal modello")
            
        except Exception as e:
            print(f"DEBUG: Unexpected error in send_message: {e}")
            # Per qualsiasi altra eccezione
            if self.stop_event.is_set():
                self.generation_stopped.emit()
            else:
                self.error_occurred.emit(f"Errore imprevisto: {str(e)}")


class ConnectionMonitor(QThread):
    """Monitor per lo stato della connessione"""
    
    connection_changed = pyqtSignal(bool)
    
    def __init__(self, request_manager: RequestManager, parent=None):
        super().__init__(parent)
        self.request_manager = request_manager
        self.check_interval = 30  # secondi
        self.last_status = None
    
    def run(self):
        """Loop di monitoring"""
        while not self.isInterruptionRequested():
            try:
                current_status = self.request_manager.test_connection()
                
                if current_status != self.last_status:
                    self.connection_changed.emit(current_status)
                    self.last_status = current_status
                
                self.msleep(self.check_interval * 1000)
                
            except Exception:
                if self.last_status is not False:
                    self.connection_changed.emit(False)
                    self.last_status = False
                self.msleep(5000)  # Retry più frequente in caso di errore