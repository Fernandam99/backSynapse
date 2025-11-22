from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .rol import Rol
from .usuario import Usuario
from .usuario_sala import UsuarioSala
from .tecnica import Tecnica
from .tarea import Tarea
from .sesiontecnicaparam import SesionTecnicaParam
from .sesion import Sesion
from .sala import Sala
from .sala_sesion import SalaSesion
from .recompensa import Recompensa
from .recompensa_usuario import RecompensaUsuario
from .progreso import Progreso

__all__ = ['db', 'Rol', 'Usuario', 'UsuarioSala','Tecnica','Tarea','SesionTecnicaParam','Sesion','Sala','SalaSesion','Recompensa','RecompensaUsuario','Progreso'] 