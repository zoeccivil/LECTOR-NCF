"""
Async helper for Firebase operations using QThread
"""
from PyQt6.QtCore import QThread, pyqtSignal
from typing import Callable, Any


class FirebaseWorker(QThread):
    """
    Worker thread for asynchronous Firebase operations
    Prevents UI freezing during database operations
    """
    data_loaded = pyqtSignal(object)  # Emits result data
    error_occurred = pyqtSignal(str)  # Emits error message
    
    def __init__(self, method: Callable, *args, **kwargs):
        """
        Initialize worker thread
        
        Args:
            method: Firebase method to call
            *args: Positional arguments for the method
            **kwargs: Keyword arguments for the method
        """
        super().__init__()
        self.method = method
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Execute the Firebase method in a separate thread"""
        try:
            result = self.method(*self.args, **self.kwargs)
            self.data_loaded.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))


class FirebaseWorkerPool:
    """
    Pool to manage multiple Firebase worker threads
    Keeps track of active workers to prevent premature garbage collection
    """
    
    def __init__(self):
        self.active_workers = []
    
    def execute(self, method: Callable, on_success: Callable = None, 
                on_error: Callable = None, *args, **kwargs):
        """
        Execute a Firebase method asynchronously
        
        Args:
            method: Firebase method to call
            on_success: Callback for successful execution
            on_error: Callback for errors
            *args: Positional arguments for the method
            **kwargs: Keyword arguments for the method
        """
        worker = FirebaseWorker(method, *args, **kwargs)
        
        if on_success:
            worker.data_loaded.connect(on_success)
        
        if on_error:
            worker.error_occurred.connect(on_error)
        
        # Cleanup when finished
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        
        self.active_workers.append(worker)
        worker.start()
    
    def _cleanup_worker(self, worker):
        """Remove worker from active list when finished"""
        if worker in self.active_workers:
            self.active_workers.remove(worker)
